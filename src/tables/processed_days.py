from .table import Table
from sqlalchemy.engine.base import Engine
from sqlalchemy.exc import SQLAlchemyError
import datetime

class Processed_Days(Table):

    def __init__(self, user=None, passwd=None, hostname="localhost", db_name="aperture", verbose=False, engine=None):
        super().__init__(user, passwd, hostname, db_name, verbose, engine)
        self._table_name = "processed_days"
        self._index_col = "day"
        self._expected_cols = [
        ]
        self._creation_sql = "".join(["""
            CREATE TABLE IF NOT EXISTS """, self._schema, ".", self._table_name, """
            (
                day DATE PRIMARY KEY
            );"""])

    #######################################################

    # This method will take string(s) day and end_date (optional) in YYYY/MM/DD
    # as well as inserting all the dates between the two if end_date is used.
    # Inserting the various dates will be a single transaction.
    def insert(self, day, end_date=None):
        if not isinstance(self._engine, Engine):
            self._print("ERROR: invalid engine.")
            return False

        values_sql = self._create_insert_values(day, end_date)
        sql = "".join(["INSERT INTO ", self._schema, ".", self._table_name,
                       " (", self._index_col, ") VALUES ",
                       values_sql,
                       ";"])
        self._print(sql)
        try:
            self._print("Connecting to DB.")
            conn = self._engine.connect()
            conn.execute(sql)
        except SQLAlchemyError as error:
            print("SQLAlchemyError: ", error)
            return False
        self._print("Done")
        return True

    #######################################################

    # This method will take string(s) day and end_date (optional) in YYYY/MM/DD
    # as well as deleting all the dates between the two if end_date is used.
    # Deleting the various dates will be a single transaction.
    # NOTE: This will only return False on a botched SQL, not as to the delete
    # operation.
    def delete(self, day):
        if not isinstance(self._engine, Engine):
            self._print("ERROR: invalid engine.")
            return False

        date = None
        try:
            date = datetime.datetime.strptime(day, "%Y-%m-%d")
        except ValueError:
            self._print("Error: The input date is malformed; please use the YYYY-MM-DD format.")
            return False

        sql = "".join(["DELETE FROM ", self._schema, ".", self._table_name,
                       " WHERE day='", str(date.year), "/", str(date.month), "/", str(date.day),
                       "';"])
        self._print(sql)
        try:
            self._print("Connecting to DB.")
            conn = self._engine.connect()
            conn.execute(sql)
        except SQLAlchemyError as error:
            print("SQLAlchemyError: ", error)
            return False
        self._print("Done")
        return True

    #######################################################

    def _create_insert_values(self, day, end_date):
        dates = []
        try:
            dates.append(datetime.datetime.strptime(day, "%Y-%m-%d"))
            if end_date is not None:
                end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
                delta = datetime.timedelta(days=1)
                curr_date = dates[0]
                curr_date += delta
                while curr_date < end_date:
                    dates.append(curr_date)
                    curr_date += delta
                dates.append(end_date)
        except ValueError:
            self._print("Error: The input date is malformed; please use the YYYY-MM-DD format.")
            return False

        values_sql = []
        for date in dates:
            values_sql.append(
                "".join(["('", str(date.year), "/", str(date.month), "/", str(date.day), "')"])
            )
        return ", ".join(values_sql)
