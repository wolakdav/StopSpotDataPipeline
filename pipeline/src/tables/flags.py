import pandas

from .table import Table

import flaggers.flagger as flagger

class Flags(Table):

    def __init__(self, user=None, passwd=None, hostname=None, db_name=None, schema="hive", verbose=False, engine=None):
        super().__init__(user, passwd, hostname, db_name, schema, verbose, engine)
        self._table_name = "flags"
        self._index_col = None
        # flag_id will be explicitly set by flag's enum values rather than
        # auto increment. This prevents strange duplicate flags with different
        # id when changing the flag enums.
        self._expected_cols = [
            "flag_id",
            "description"
        ]
        self._creation_sql = "".join(["""
            CREATE TABLE IF NOT EXISTS """, self._schema, ".", self._table_name, """
            (
                flag_id INTEGER PRIMARY KEY,
                description VARCHAR(200)
            );"""])


    def write_table(self, flags):
        # flags is a list of [flag_id, flag_name]
        df = pandas.DataFrame(flags, columns=self._expected_cols)
        return self._write_table(df, conflict_columns=["flag_id"])


    def create_table(self):
        # Flags are written into the database on creation.
        if not super().create_table():
            return False

        flags = []
        for flag in flagger.Flags:
            flags.append([flag.value, flagger.flag_descriptions[flag]])

        self.write_table(flags)
        return 

    def write_csv(self, path):
        """
        Function is meant to be called by a subclass: saves passed in data to a csv file.

        Args: 
            path    (String): relative path to where csv will be saved. 

        Returns: 
            Boolean representing state of the operation (successfull write: True, error during process: False)
        """

        flags = []

        #Append expected cols first to create header row in the csv file
        flags.append(self._expected_cols)

        #Create list with all flag data
        for flag in flagger.Flags:
            flags.append([flag.value, flagger.flag_descriptions[flag]])

        #Create pandas DataFrame from the list
        df = pandas.DataFrame(flags)

        #Call parent function that does actual saving
        return super().write_csv(df, path)


