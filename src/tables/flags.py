import pandas

from .table import Table

import flaggers.flagger as flagger

class Flags(Table):

    def __init__(self, user=None, passwd=None, hostname="localhost", db_name="aperture", verbose=False, engine=None):
        super().__init__(user, passwd, hostname, db_name, verbose, engine)
        self._table_name = "flags"
        self._index_col = "flag_id"
        self._expected_cols = set([
            "description"
        ])
        self._creation_sql = "".join(["""
            CREATE TABLE IF NOT EXISTS """, self._schema, ".", self._table_name, """
            (
                flag_id INTEGER PRIMARY KEY,
                description VARCHAR(200)
            );"""])


    def write_table(self, flags, append=True):
        # flags is a list of flag names
        df = pandas.DataFrame(flags, columns=['description'])
        return self._write_table(df, append)


    def create_table(self):
        # Flags are written into the database on creation.
        if not super().create_table():
            return False

        flags = []
        for flag in flagger.Flags:
            flags.append(flagger.flag_descriptions[flag])

        self.write_table(flags, append=True)
        return True
