import datetime
from sqlalchemy.engine.base import Engine
from sqlalchemy.exc import SQLAlchemyError
import pandas
from .table import Table


class Flagged_Data(Table):

    def __init__(self, user=None, passwd=None, hostname=None, db_name=None, verbose=False, engine=None):
        super().__init__(user, passwd, hostname, db_name, verbose, engine)
        self._table_name = "flagged_data"
        self._index_col = None
        self._expected_cols = [
            "row_id",
            "service_key",
            "flag_id",
            "date_computed"
        ]
        # flag_id is ON UPDATE CASCADE to anticipate flags table changing.
        # service_key shouldn't change.
        self._creation_sql = "".join(["""
            CREATE TABLE IF NOT EXISTS """, self._schema, ".", self._table_name, """
            (
                row_id INTEGER,
                service_key INTEGER REFERENCES """, self._schema, """.service_periods(service_key),
                flag_id INTEGER REFERENCES """, self._schema, """.flags(flag_id) ON UPDATE CASCADE,
                date_computed DATE NOT NULL,
                PRIMARY KEY (flag_id, service_key, row_id)
            );"""])

    #######################################################

    def write_table(self, data):
        # data is list of [row_id, flag_id, service_key].
        if data == []:
            self._print("ERROR: write_table recieved no data to write, cancelling.")
            return False
        df = pandas.DataFrame(data, columns=[
            "row_id",
            "service_key",
            "flag_id",
            ])
        df["date_computed"] = datetime.datetime.now().date().strftime("%Y/%m/%d")
        print(df)
        return self._write_table(df, 
                 conflict_columns=["row_id", "flag_id", "service_key"])

    #######################################################

# SELECT *
# FROM
#      aperture.flagged_data AS fd,
#      aperture.service_periods AS sp
# WHERE
#       fd.row_id = '10'
# AND
#       sp.year = '2019'
# AND
#       sp.ternary = '1'
# AND
#       fd.service_key = sp.service_key;
    def query_by_row_id(self, sp_table, row_id, service_year, service_period):
        sql = "".join(["SELECT * FROM ",
                       self._schema,
                       ".",
                       self._table_name,
                       " AS fd, ",
                       self._schema,
                       ".",
                       sp_table,
                       " AS sp, WHERE fd.row_id = '",
                       row_id,
                       "' AND sp.year = '",
                       service_year,
                       "' AND sp.ternary = '",
                       service_period,
                       "' AND fd.service_key = sp.service_key"
                       ";"])

        return self._query_table(sql)

    #######################################################

    def query_by_flag_id(self, flag_id, limit):
        sql = "".join(["SELECT * FROM ",
                       self._schema,
                       ".",
                       self._table_name,
                       " WHERE flag_id = '",
                       flag_id,
                       "' LIMIT '",
                       limit,
                       "';"])

        return self._query_table(sql)

    #######################################################

    # Return the latest day (as datetime) stored, None if no days are stored.
    # TODO: update
    def get_latest_day(self):
        value = None
        sql = "".join(["SELECT MAX(", self._index_col, ")",
                       "FROM ", self._schema, ".", self._table_name,
                       ";"])
        self._print(sql)
        try:
            self._print("Connecting to DB.")
            conn = self._engine.connect()
            value = conn.execute(sql)
        except SQLAlchemyError as error:
            print("SQLAlchemyError: ", error)
            return None
        
        if value is not None:
            self._print("Done")
            return value.first()[0]
        else:
            return None

    #######################################################

    def delete_date_range(self, start_date, end_date=None):
        if end_date is None:
            end_date = start_date
        pass # TODO: this

    #######################################################

    # Get a list of date value(s) b/w day and end_date.
    # day and end_date can be strings in YYYY/MM/DD or datetime instances.
    def _get_date_range(self, day, end_date=None):
        dates = []
        try:
            if not isinstance(day, datetime.date):
                dates.append(datetime.datetime.strptime(day, "%Y-%m-%d"))
            else:
                dates.append(day)
            if end_date is not None:
                if not isinstance(end_date, datetime.date):
                    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
                delta = datetime.timedelta(days=1)
                curr_date = dates[0]
                curr_date += delta
                while curr_date < end_date:
                    dates.append(curr_date)
                    curr_date += delta
                dates.append(end_date)
        except ValueError:
            self._print("ERROR: The input date is malformed; please use the YYYY-MM-DD format.")
            return None

        return dates
