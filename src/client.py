import os
import sys
from datetime import datetime
from datetime import timedelta
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

from src.ios import IOs
from src.tables import CTran_Data
from src.tables import Flagged_Data
from src.tables import Flags
from src.tables import Service_Periods
from src.config import config
from src.interface import ArgInterface
from flaggers.flagger import flaggers


class _Option():
    def __init__(self, msg, func_pointer):
        self.msg = msg
        self.func_pointer = func_pointer


""" Members:
self.config
self. tables
self._hive_engine
self._portal_engine
"""
class _Client(IOs):
    def __init__(self, read_env_data=True, verbose=True):
        super().__init__(verbose)
        try:
            if not read_env_data and os.environ["PIPELINE_ENV_DATA"]:
                read_env_data = True
        except KeyError as err:
            pass

        self.config = config
        self.config.load(read_env_data=read_env_data)

        portal_user = config.get_value('portal_user')
        portal_passwd = config.get_value('portal_passwd')
        portal_hostname = config.get_value('portal_hostname')
        portal_db_name = config.get_value('portal_db_name')
        if portal_user and portal_passwd and portal_hostname and portal_db_name:
            self.ctran = CTran_Data(portal_user, portal_passwd, portal_hostname, portal_db_name, verbose=verbose)
        else:
            print("Please enter credentials for Portal's database with the C-Tran table.")
            self.ctran = CTran_Data(verbose=verbose)
        self._portal_engine = self.ctran.get_engine()

        pipe_user = config.get_value('pipeline_user')
        pipe_passwd = config.get_value('pipeline_passwd')
        pipe_hostname = config.get_value('pipeline_hostname')
        pipe_db_name = config.get_value('pipeline_db_name')
        if pipe_user and pipe_passwd and pipe_hostname and pipe_db_name:
            self.flagged = Flagged_Data(pipe_user, pipe_passwd, pipe_hostname, pipe_db_name, verbose=verbose)
        else:
            print("Please enter credentials for Hive's Database.")
            self.flagged = Flagged_Data(verbose=verbose)

        self._hive_engine = self.flagged.get_engine()
        engine_url = self._hive_engine.url
        self.flags = Flags(verbose=verbose, engine=engine_url)
        self.service_periods = Service_Periods(verbose=verbose, engine=engine_url)

    #######################################################

    def main(self, read_env_data=False):

        if len(sys.argv) > 1:
            ai = ArgInterface()
            return ai.query_with_args(self.ctran, self.flagged, sys.argv[1:])

        options = [
            _Option("(or ctrl-d) Exit.", lambda: "Exit"),
            _Option("[dev tool] Create Aperature, the Portal mock DB [dev tool].",
                        self.ctran.create_table),
            _Option("Create Hive, the output point of the Data Pipeline.",
                        self.create_hive),
            _Option("Process data from Portal (Which currently is Aperture)",
                        self.process_data),
            _Option("Sub-menu: DB Operations",
                        self._db_menu),
        ]

        self._menu("Welcome to the CTran Data Marking Pipeline.", options)

    #######################################################

    def create_hive(self):
        self.flags.create_table()
        self.service_periods.create_table()
        self.flagged.create_table()

    ###########################################################

    # Process data between start_date and end_date, inclusive. These parameters
    # can be date instances or strings in format "YYYY/MM/DD". If no dates are
    # supplied, this will prompt the user for them.
    # TODO: update parameter default values
    def process_data(self, start_date="", end_date=""):
        self.print("Starting data processing pipeline.")
        ctran_df = None
        if start_date == "" or end_date == "":
            date_range = self._get_date_range()
            ctran_df = self.ctran.query_date_range(*date_range)
        else:
            ctran_df = self.ctran.query_date_range(start_date, end_date)

        if ctran_df is None:
            self.print("ERROR: the supplied dates were unable to be gathered from CTran data.")
            return False

        flagged_rows = []
        # TODO: Stackoverflow is telling me iterrows is a slow way of iterrating,
        # but i'll leave optimizing for later.
        i = 0 # TODO: delete this
        for row_id, row in ctran_df.iterrows():
            i += 1 # TODO: delete this
            print(i) # TODO: delete this
            if i > 100: # TODO: delete this
                break # TODO: delete this
            month = row.service_date.month
            year = row.service_date.year
            service_key = self.service_periods.query_or_insert(month, year)

            # If this fails, it's very likely a sqlalchemy error.
            # e.g. not able to connect to db.
            if not service_key:
                self.print("ERROR: cannot find or create new service_key, skipping.")
                continue

            flags = set()
            for flagger in flaggers:
                try:
                    # Duplicate flagger requires a special call.
                    if flagger.name == "Duplicate":
                        flags.update(flagger.flag(row_id, ctran_df))
                    else:
                        flags.update(flagger.flag(row))
                except Exception as e:
                    self.print("WARNING: error in flagger {}. Skipping.\n{}"
                        .format(flagger.name, e))

            for flag in flags:
                flagged_rows.append([row_id, service_key, int(flag)])

        self.flagged.write_table(flagged_rows)
        self.print("Done.")
        return True

    ###########################################################

    # This method will process all days since the latest processed day.
    def process_since_checkpoint(self):
        start_date = self.processed_days.get_latest_day()
        self._print("Last processed day: " + str(start_date))
        start_date = start_date + timedelta(days=1)
        self._print("Processing from:  " + str(start_date))
        end_date = datetime.now().date()
        self._print("\t   until: " + str(end_date))
        return self.process_data(start_date, end_date)

    ###########################################################
    
    # This method will process the next day after the latest processed day.
    def process_next_day(self):
        start_date = self.processed_days.get_latest_day()
        self._print("Last processed day: " + str(start_date))
        start_date = start_date + timedelta(days=1)
        self._print("Processing from:  " + str(start_date))
        end_date = start_date
        self._print("\t   until: " + str(end_date))
        return self.process_data(start_date, end_date)

    ###########################################################

    def reprocess(self, start_date, end_date=None):
        pass # TODO: this

    ###########################################################

    def _db_menu(self):
        def ctran_info():
            query = self.ctran.get_full_table()
            if query is None:
                self.print("WARNING: no data returned.")
            else:
                query.info()

        options = [
            _Option("(or ctrl-d) Exit.", lambda: "Exit"),
            _Option("Print engine.", lambda: print(self.flagged.get_engine())),
            _Option("[dev tool] Create aperture schema [dev tool].", self.ctran.create_schema),
            _Option("[dev tool] Delete aperture schema [dev tool].", self.ctran.delete_schema),
            _Option("[dev tool] Create mock ctran_data table [dev tool].", self.ctran.create_table),
            _Option("[dev tool] Delete mock ctran_data table [dev tool].", self.ctran.delete_table),
            _Option("Create hive schema.", self.flags.create_schema),
            _Option("Delete hive schema.", self.flags.delete_schema),
            _Option("Create flagged_data table.", self.flagged.create_table),
            _Option("Create flags table.", self.flags.create_table),
            _Option("Create service_periods table.", self.service_periods.create_table),
            _Option("Delete flagged_data table.", self.flagged.delete_table),
            _Option("Delete service_periods table.", self.flags.delete_table),
            _Option("Query ctran_data and print ctran_data.info().", ctran_info)
        ]

        return self._menu("This is the Database Operations sub-menu.", options)

    ###########################################################

    # Option.func_pointer should return str "Exit" iff that option should cause
    # the menu it is in to exit.
    def _menu(self, title, options):
        if len(options) == 0:
            return

        msg = " ".join([str(title), "Please select what you would like to do:"])
        should_exit = False
        while not should_exit:
            print()
            print(msg)
            print()
            print()
            for i in range(len(options)):
                print(str(i) + ": " + options[i].msg)
            print()

            option = None
            try:
                option = self._get_menu_option(0, len(options)-1)
            except EOFError:
                option = 0

            if options[option].func_pointer() == "Exit":
                should_exit = True

    ###########################################################

    def _get_menu_option(self, min_value, max_value, cli_symbol="> "):
        should_continue = True
        while should_continue:
            try:
                option = input(cli_symbol)
                option = int(option)

                if option < min_value or option > max_value:
                    print("{" + str(option) + "} is not within range [" + str(min_value) + ", " + str(max_value) + "]; try again.")
                else:
                    should_continue = False

            except ValueError:
                print("Please enter an integer.")

        return option

    ###########################################################

    # If the user inputs the start and end dates backwards, this will flip them on
    # return.
    def _get_date_range(self):
        def _get_valid_date(criteria):
            while True:
                date = self.prompt("Please enter the " + criteria + " date (YYYY-MM-DD): ")
                try:
                    date = datetime.strptime(date, "%Y-%m-%d")
                except ValueError:
                    print("\tThe input date is malformed; please use the YYYY-MM-DD format.")
                else:
                    return date


        start_date = _get_valid_date("start")
        end_date   = _get_valid_date("end  ")

        if start_date < end_date:
            return (start_date, end_date)
        else:
            return (end_date, start_date)


###############################################################################

client_instance = _Client()
