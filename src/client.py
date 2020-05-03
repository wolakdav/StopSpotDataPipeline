# NOTE: This file will have the below available to work if the file is ran with
# $ python3 -i main.py
# ctran
# flagged
# flags
# service_periods
# processed_days
# TODO: support this ^^ comment in main; yes, all public members of _Client
import os
import sys
from datetime import datetime

from src.ios import IOs
from src.tables import CTran_Data
from src.tables import Flagged_Data
from src.tables import Flags
from src.tables import Service_Periods
from src.tables import Processed_Days
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
self._transaction_in_progress
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
        self._transaction_in_progress = False

        user = config.get_value('pipeline_user')
        passwd = config.get_value('pipeline_passwd')
        hostname = config.get_value('pipeline_hostname')
        db_name = config.get_value('pipeline_db_name')

        if user and passwd and hostname and db_name:
            self.ctran = CTran_Data(user, passwd, hostname, db_name, verbose=True)
        else:
            self.ctran = CTran_Data(verbose=True)

        engine_url = self.ctran.get_engine().url
        self.flagged = Flagged_Data(verbose=True, engine=engine_url)
        self.flags = Flags(verbose=True, engine=engine_url)
        self.service_periods = Service_Periods(verbose=True, engine=engine_url)
        self.processed_days = Processed_Days(verbose=True, engine=engine_url)

    #######################################################

    def main(self, read_env_data=False):
        def create_hive():
            self.flags.create_table()
            self.service_periods.create_table()
            self.flagged.create_table()
            self.processed_days.create_table()

        if len(sys.argv) > 1:
            ai = ArgInterface()
            return ai.query_with_args(self.ctran, self.flagged, sys.argv[1:])

        options = [
            _Option("(or ctrl-d) Exit.", lambda: "Exit"),
            _Option("[dev tool] Create Aperature, the Portal mock DB [dev tool].",
                        self.ctran.create_table),
            _Option("Create Hive, the output point of the Data Pipeline.",
                        create_hive),
            _Option("Process data from Portal (Which currently is Aperture)",
                        self.process_data),
            _Option("Sub-menu: DB Operations",
                        self._db_menu),
        ]

        self._menu("Welcome to the CTran Data Marking Pipeline.", options)

    ###########################################################

    # TODO: make this more descriptive
    # YYYY/MM/DD
    # Missing date(s) -> prompt for dates
    def process_data(self, start_date="", end_date=""):
        ctran_df = None
        if start_date == "" or end_date == "":
            date_range = self._get_date_range()
            ctran_df = self.ctran.query_date_range(*date_range)
        else:
            ctran_df = self.ctran.query_date_range(start_date, end_date)

        if ctran_df is None:
            print("ERROR: the supplied dates were unable to be gathered from CTran data.")
            return False

        flagged_rows = []
        # TODO: Stackoverflow is telling me iterrows is a slow way of iterrating,
        # but i'll leave optimizing for later.
        i = 0
        for row_id, row in ctran_df.iterrows():
            i += 1
            print(i)
            if i > 100:
                break
            month = row.service_date.month
            year = row.service_date.year
            service_key = self.service_periods.query_or_insert(month, year)

            # If this fails, it's very likely a sqlalchemy error.
            # e.g. not able to connect to db.
            if not service_key:
                print("ERROR: cannot find or create new service_key, skipping.")
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
                    print("WARNING: error in flagger {}. Skipping.\n{}"
                        .format(flagger.name, e))

            for flag in flags:
                flagged_rows.append([row_id, service_key, int(flag)])

        self.flagged.write_table(flagged_rows)
        self.processed_days.insert(start_date, end_date)

    ###########################################################

    def process_since_checkpoint(self):
        pass # TODO: this

    ###########################################################
    
    def process_next_day(self):
        pass # TODO: this

    ###########################################################

    def _db_menu(self):
        def ctran_info():
            query = ctran.get_full_table()
            if query is None:
                print("WARNING: no data returned.")
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
            _Option("Create processed_days table.", self.processed_days.create_table),
            _Option("Delete flagged_data table.", self.flagged.delete_table),
            _Option("Delete service_periods table.", self.flags.delete_table),
            _Option("Delete processed_days table.", self.processed_days.delete_table),
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

    ###########################################################

    def _begin_transaction(self):
        pass # TODO: this

    ###########################################################

    def _commit_transaction(self):
        pass # TODO: this

###############################################################################

client_instance = _Client()
