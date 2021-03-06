import abc
import sys
import getpass
import pandas
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.engine.base import Engine
import os

from ..ios import ios



""" Extending Table
Subclasses should not alter self._engine in any capacity.
For more, see docs/db_ops.md
"""
class Table(abc.ABC):

    ###########################################################################
    # Public Methods

    # passwd is not stored as member data, it is destroyed after use.
    def __init__(self, user=None, passwd=None, hostname=None, db_name=None, schema="hive", engine=None):
        self._ios = ios
        self._table_name = None
        self._index_col = None
        self._chunksize = 1000

        if schema is None:
            self._schema = self._ios.prompt("Enter the table's schema: ")
        else:
            self._schema = schema

        if engine is not None:
            self._engine = create_engine(engine)

        else:
            if user is None:
                user = self._ios.prompt("Enter username: ")
            if passwd is None:
                passwd = self._ios.prompt("Enter password: ", hide_input=True)
            if hostname is None:
                hostname = self._ios.prompt("Enter hostname: ")
            if db_name is None:
                db_name = self._ios.prompt("Enter the database's name: ")

            self._build_engine(user, passwd, hostname, db_name)

    #######################################################

    def get_engine(self):
        return self._engine

    #######################################################
    
    def get_full_table(self):
        if not isinstance(self._engine, Engine):
            self._ios.log_and_print("self._engine is not an Engine, cannot continue.", ios.Severity.ERROR)
            return None

        df = None
        sql = "".join(["SELECT * FROM ", self._schema, ".", self._table_name, ";"])
        self._ios.log_and_print(sql)
        try:
            df = pandas.read_sql(sql, self._engine, index_col=self._index_col)

        except SQLAlchemyError as error:
            self._ios.log_and_print("SQLAlchemy: " + str(error), ios.Severity.ERROR)
            return None
        except (KeyError, ValueError) as error:
            self._ios.log_and_print("Pandas: " + str(error), ios.Severity.ERROR)
            return None
        
        if not self._check_cols(df):
            self._ios.log_and_print("ERROR: the columns of read data does not match the specified columns.", ios.Severity.ERROR)
            return None

        return df

    #######################################################

    def create_schema(self):
        if not isinstance(self._engine, Engine):
            self._ios.log_and_print("self._engine is not an Engine, cannot continue.", ios.Severity.ERROR)
            return False

        sql = "".join(["CREATE SCHEMA IF NOT EXISTS ", self._schema, ";"])
        try:
            conn = self._engine.connect()
            self._ios.log_and_print(sql)
            conn.execute(sql)

        except SQLAlchemyError as error:
            self._ios.log_and_print("SQLAlchemy: " + str(error), ios.Severity.ERROR)
            return False

        return True

    #######################################################

    def delete_schema(self):
        if not isinstance(self._engine, Engine):
            self._ios.log_and_print("self._engine is not an Engine, cannot continue.", ios.Severity.ERROR)
            return False

        sql = "".join(["DROP SCHEMA IF EXISTS ", self._schema, " CASCADE;"])
        try:
            conn = self._engine.connect()
            self._ios.log_and_print(sql)
            conn.execute(sql)

        except SQLAlchemyError as error:
            self._ios.log_and_print("SQLAlchemy: " + str(error), ios.Severity.ERROR)
            return False

        return True

    #######################################################
    
    def create_table(self):
        if not isinstance(self._engine, Engine):
            self._ios.log_and_print("self._engine is not an Engine, cannot continue.", ios.Severity.ERROR)
            return False

        if not self.create_schema():
            self._ios.log_and_print("Failed to create schema, cancelling operation", ios.Severity.ERROR)
            return False

        try:
            conn = self._engine.connect()
            self._ios.log_and_print(self._creation_sql)
            conn.execute(self._creation_sql)

        except SQLAlchemyError as error:
            self._ios.log_and_print("SQLAlchemy: " + str(error), ios.Severity.ERROR)
            return False

        return True

    #######################################################
    

    def delete_table(self):
        if not isinstance(self._engine, Engine):
            self._ios.log_and_print("self._engine is not an Engine, cannot continue.", ios.Severity.ERROR)
            return False

        sql = "".join(["DROP TABLE IF EXISTS " + self._schema + "." + self._table_name + ";"])
        try:
            conn = self._engine.connect()
            self._ios.log_and_print(sql)
            conn.execute(sql)

        except SQLAlchemyError as error:
            self._ios.log_and_print("SQLAlchemy: " + str(error), ios.Severity.ERROR)
            return False

        return True

    ###########################################################################
    # Protected Methods

    def _write_table(self, df, conflict_columns=None):
        # Write the given dataframe into the database.
        # This method is meant to be called by a subclass.
        # df should be a well formed DataFrame, the subclass should form
        # the DataFrame.
        # conflict_columns should be a list of str values used as primary keys.
        #   if conflict_columns is None, will not do ON CONFLICT.
        #   ON CONFLICT is always set to DO NOTHING. This is to ensure there
        #   are no errors when inserting a duplicate row.
        #
        # TODO: Add an update option to ON CONFLICT.
        # Currently ON CONFLICT only exists to stop postgres from
        # throwing a fit whenever there's a duplicate insert. Would be useful
        # to have an option to overwrite the duplicate data instead.
        # Will be very useful for updating the flags table without dropping
        # the whole thing.

        if not self._table_name:
            self._ios.log_and_print(
                "_write_table not called by a subclass.", ios.Severity.ERROR)
            return False

        if not isinstance(self._engine, Engine):
            self._ios.log_and_print("invalid engine", ios.Severity.ERROR)
            return False

        if not self._check_cols(df):
            self._ios.log_and_print(
                "the columns of data does not match required columns",
                ios.Severity.ERROR)
            return False

        self._ios.log_and_print("Writing to table.")

        columns = ", ".join(list(df))
        # (value1, value2, ...), (value1, value2, ...), ...
        values = ", ".join(["{}".format(tuple(row)) 
                            for row in df.values.tolist()])

        sql = "".join(["INSERT INTO ", self._schema, ".", self._table_name,
                       " (", columns, ") VALUES ", values])

        self._ios.log_and_print("".join([
            "Writing to: ", self._schema, ".", self._table_name]))

        if conflict_columns:
            conflict_columns = "({})".format(
                               ", ".join([s for s in conflict_columns]))
            sql += "".join([" ON CONFLICT ", conflict_columns, " DO NOTHING;"])

        try:
            con = self._engine.connect()
            # This /doesn't/ log the SQL here as opposed to how it usually is
            # because that would blow away the terminanl and make the file
            # extremely hard to read and needlessly long.
            con.execute(sql)
        except SQLAlchemyError as error:
            self._ios.log_and_print(
                "SQLAlchemyError: " + str(error).splitlines()[0],
                ios.Severity.ERROR)
            return False

        return True

    #######################################################

    def _check_cols(self, sample_df):
        # Check the columns of input df to make sure it matches what we expect.

        # We may or may not care about the order of the columns. If not, then
        # wrap both sides in set().
        if set(list(sample_df)) != set(self._expected_cols):
            return False

        return True

    #######################################################

    """
    Queries the C-Tran data table using the given SQL query.

    :argument   a SQL query string
    :returns    a DataFrame containing query results, or
                None if an exception occurred.
    """
    def _query_table(self, sql):
        if not isinstance(self._engine, Engine):
            self._ios.log_and_print("invalid engine", ios.Severity.ERROR)
            return None

        df = None
        self._ios.log_and_print(sql)
        try:
            df = pandas.read_sql(sql, self._engine, index_col=self._index_col)

        except SQLAlchemyError as error:
            self._ios.log_and_print("SQLAlchemy: " + str(error), ios.Severity.ERROR)
            return None
        except (ValueError, KeyError) as error:
            self._ios.log_and_print("Pandas: " + str(error), ios.Severity.ERROR)
            return None

        if not self._check_cols(df):
            self._ios.log_and_print("the columns of read data does not match the specified columns" , ios.Severity.ERROR)
            return None

        #Converts NaN to None, can't do the same with NaT: null flagger takes care
        df1 = df.where(df.notnull(), None)

        return df1

    ###########################################################################
    # Private Methods

    def _build_engine(self, user, passwd, hostname, db_name):
        engine_info = ["postgresql://", user, ":", passwd, "@", hostname, "/", db_name]
        self._engine = create_engine("".join(engine_info))
        
        self._ios.log_and_print("Your engine has been created: ", obj=self._engine)
        return True

    ###########################################################################

    def write_csv(self, df, path):
        """
        Function is meant to be called by a subclass: saves passed in data to a csv file.

        Args: 
            df      (Object): pandas DataFrame that contains data to be saved to a csv.
            path    (String): relative path to where csv will be saved. 

        Returns: 
            Boolean representing state of the operation (successfull write: True, error during process: False)
        """

        #Check that function is called by a subclass
        if not self._table_name:
            self._print("ERROR: write_csv not called by a subclass.")
            return False

        #Pandas to_csv doesn't take care of path creation, thus check if path actually exists, and if not: create it
        if not os.path.exists(path):
            os.mkdir(path)

        #Create full path to where data will be saved
        full_path = "" + path + self._table_name + ".csv"

        #Attempt saving
        try:
            df.to_csv(full_path, index=False, encoding='utf-8')
        except:
            self._print("ERROR: write_csv couldn't save data to " + full_path)
            return False

        return True

