from .table import Table

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

    def add_day(self, day):
        pass

    def delete_day(self, day):
        pass