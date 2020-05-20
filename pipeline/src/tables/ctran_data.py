import sys
import pandas
from .table import Table
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.engine.base import Engine

class CTran_Data(Table):

    ###########################################################################
    # Public Methods

    def __init__(self, user=None, passwd=None, hostname=None, db_name=None, schema="aperture", engine=None):
        super().__init__(user, passwd, hostname, db_name, schema, engine)
        self._table_name = "ctran_data"
        self._index_col = "row_id"
        self._expected_cols = [
            "service_date",
            "vehicle_number",
            "leave_time",
            "train",
            "route_number",
            "direction",
            "service_key",
            "trip_number",
            "stop_time",
            "arrive_time",
            "dwell",
            "location_id",
            "door",
            "lift",
            "ons",
            "offs",
            "estimated_load",
            "maximum_speed",
            "train_mileage",
            "pattern_distance",
            "location_distance",
            "x_coordinate",
            "y_coordinate",
            "data_source",
            "schedule_status",
            "trip_id"
        ]

        self._creation_sql = "".join(["""
            CREATE TABLE IF NOT EXISTS """, self._schema, ".", self._table_name, """
            (
                row_id BIGSERIAL PRIMARY KEY,
                service_date DATE,
                vehicle_number INTEGER,
                leave_time INTEGER,
                train INTEGER,
                route_number INTEGER,
                direction SMALLINT,
                service_key CHARACTER(1),
                trip_number INTEGER,
                stop_time INTEGER,
                arrive_time INTEGER,
                dwell INTEGER,
                location_id INTEGER,
                door INTEGER,
                ons INTEGER,
                offs INTEGER,
                estimated_load INTEGER,
                lift INTEGER,
                maximum_speed INTEGER,
                train_mileage FLOAT,
                pattern_distance FLOAT,
                location_distance FLOAT,
                x_coordinate FLOAT,
                y_coordinate FLOAT,
                data_source INTEGER,
                schedule_status INTEGER,
                trip_id INTEGER
            );"""])

    #######################################################

    # [dev tool]
    # This will create a mock CTran Table for development purposes.
    # Updated function so that sample name can be passed: used for end-to-end testing, where separate test data needs to be loaded
    def create_table(self, ctran_sample_path="assets/", ctran_sample_name="ctran_trips_sample.csv", exists_action="append"):
        if not isinstance(self._engine, Engine):
            self._ios._print("ERROR: self._engine is not an Engine, cannot continue.")
            return False

        csv_location = "".join([ctran_sample_path, ctran_sample_name])
        self._ios._print("Loading " + csv_location)

        sample_data = None
        try:
            sample_data = pandas.read_csv(csv_location, parse_dates=["service_date"])

        except (FileNotFoundError, ValueError) as error:
            print("Pandas:", error)
            print("Cannot continue table creation, cancelling.")
            return False

        if not self._check_cols(sample_data):
            self._ios._print("ERROR: the columns of read data does not match the specified columns.")
            return False

        if not self._create_table_helper(sample_data, exists_action):
            return False

        self._ios._print("Done.")
        return True

    #######################################################

    # Query all data between date_from and date_to, dates
    # NOTE: if there is no ctran_data table, this will not work, obviously.
    def query_date_range(self, date_from, date_to):
        sql = "".join(["SELECT * FROM ",
                       self._schema,
                       ".",
                       self._table_name,
                       " WHERE service_date BETWEEN '",
                       date_from.strftime("%Y-%m-%d"),
                       "' AND '",
                       date_to.strftime("%Y-%m-%d"),
                       "';"])

        return self._query_table(sql)

    ###########################################################################
    # Private Methods

    def _create_table_helper(self, sample_data, exists_action="append"):
        self._ios._print("Connecting to DB.")
        try:
            conn = self._engine.connect()
            self._ios._print("Initializing table.")
            if not super().create_table():
                self._ios._print("ERROR: failed to create the table; cannot proceed.")
                return False

            self._ios._print("Writing sample data to table. This will take a few minutes.")

            sample_data.to_sql(
                    self._table_name,
                    self._engine,
                    if_exists = exists_action,
                    index = False,
                    chunksize = self._chunksize,
                    schema = self._schema,
                )

        except SQLAlchemyError as error:
            print("SQLAclchemy:", error)
            return False
        except (KeyError, ValueError) as error:
            print("Pandas:", error)
            return False

        return True
