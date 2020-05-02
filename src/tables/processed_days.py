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

    # This method will take string `day` in format YYYY/MM/DD and insert it to
    # table processed_days.
    def add_day(self, day):
        if not isinstance(self._engine, Engine):
            self._print("ERROR: invalid engine.")
            return False

        date = None
        try:
            date = datetime.datetime.strptime(day, "%Y-%m-%d")
        except ValueError:
            self._print("Error: The input date is malformed; please use the YYYY-MM-DD format.")
            return False

        sql = "".join(["INSERT INTO ", self._schema, ".", self._table_name,
                       " (", self._index_col, ") VALUES ('",
                        str(date.year), "/", str(date.month), "/", str(date.day),
                        "');"])
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

    # This method will take string `day` in format YYYY/MM/DD and remove it
    # from table processed_days.
    def delete_day(self, day):
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
