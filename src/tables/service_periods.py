import pandas

from .table import Table
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.engine.base import Engine

class Service_Periods(Table):

    def __init__(self, user=None, passwd=None, hostname=None, db_name=None, schema="hive", verbose=False, engine=None):
        super().__init__(user, passwd, hostname, db_name, schema, verbose, engine)
        self._table_name = "service_periods"
        self._index_col = "service_key"
        self._expected_cols = [
            "month",
            "year",
            "ternary"
        ]
        self._creation_sql = "".join(["""
            CREATE TABLE IF NOT EXISTS """, self._schema, ".", self._table_name, """
            (
                service_key BIGSERIAL PRIMARY KEY,
                month SMALLINT NOT NULL CHECK ( (month <= 12) AND (month >= 1) ),
                year SMALLINT NOT NULL CHECK (year > 1700),
                ternary SMALLINT NOT NULL CHECK ( (ternary <= 3) AND (ternary >= 1) ),
                UNIQUE (month, year, ternary)
            );"""])

    
    def write_table(self, dates):
        # Dates: list of datetime dates. Only important value in the dates are
        # month and year.
        # NOTE: not currently being used but could be useful in the future.
        data = []
        for date in dates:
            data.append([date.month, date.year, self.get_ternary(date.month)])
        df = pandas.DataFrame(data, columns=self._expected_cols)
        # service_key is BIGSERIAL so there should never be a conflict.
        return self._write_table(df)  


    def query_month_year(self, month, year):
        # Find a service_periods row that matches the month and year.
        # Note that ternary isn't included because that's derived from month.

        if not isinstance(self._engine, Engine):
            self._print("ERROR: invalid engine.")
            return None
        service_key = None

        sql = "".join(["SELECT * FROM ", self._schema, ".", self._table_name,
                       " WHERE month=", str(month), " AND year=", str(year), ";"
                       ])
        try:
            with self._engine.connect() as con:
                result = con.execute(sql)
                if result.rowcount != 0:
                    return result.first()['service_key']
        except SQLAlchemyError as error:
            print("SQLAlchemy: ", error)
            return None


    def insert_one(self, month, year):
        # Insert a row and return the id.
        # Honestly should be using write_table() but the RETURNING
        # functionality isn't built into write_table() and I'm too lazy to
        # add that functionality right now so I'll save it for a TODO.
        if not isinstance(self._engine, Engine):
            self._print("ERROR: invalid engine.")
            return None


        ternary = self.get_ternary(month)
        sql = "".join(["INSERT INTO ", self._schema, ".", self._table_name,
                       " (month, year, ternary) VALUES (",
                       str(month), ", ", str(year), ", ", str(ternary), ")",
                       " RETURNING service_key;"])
        try:
            with self._engine.connect() as con:
                result = con.execute(sql)
                return result.first()[0]
        except SQLAlchemyError as error:
            print("SQLAlchemy: ", error)
            return None


    def query_or_insert(self, month, year):
        # Retrieves the service_key of a matched service_periods.
        # If none exist, insert a new one and return its service_key.
        query = self.query_month_year(month, year)
        if query:
            return query
        
        return self.insert_one(month, year)
        

    def get_ternary(self, month):
        # Get the ternary value for a given month. 
        # These values are not confirmed by user and may change in the future.
        # Jan to Apr is 1.
        # May to Aug is 2.
        # Sep to Dec is 3.
        # Any invalid month returns a -1.
        if month < 1 or month > 12:
            return -1  # Invalid.
        date = datetime(2000, month, 1)
        if (date >= datetime(2000, 1, 1) and 
            date <= datetime(2000, 4, 1)):
            return 1
        if (date >= datetime(2000, 5, 1) and 
            date <= datetime(2000, 8, 1)):
            return 2
        else:
            return 3
        
