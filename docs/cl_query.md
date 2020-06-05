**NOTE**: Example usage is based upon accessing these features via command
line arguments.

### Starting the Client

Running `main.py` with **zero** arguments will start the command line
interactive menu. This interface provides instructions with the options
it presents. The presence of any arguments following `main.py` will trigger
command line argument handling and will not launch the interactive menu.

#

### Running the Daily Operation

Example usage: `main.py --daily`

This argument triggers the sequential fetching of the last processed date
and execution of the following day's data. This information is fetched
from the table "flagged_data" via `flagged_data.py get_latest_day`. This
is the operation utilized by the cron job, and is intended as an automated
process.

#

### Querying the Database

#### From ctran_data.py

##### `DataFrame query_date_range(date_from, date_to)`

_date_from_: starting date for selection predicate, inclusive.

_date_to_: ending date for selection predicate, inclusive.

Example usage: `main.py --date-start=YYYY-MM-DD --date-end=YYYY-MM-DD`

This queries the database for all rows in the range of the start and end
date arguments. This is purpose-built for the pickup of new data based on
the automated daily run specification, in which case start and end date
will be the same date. Note that this will collect all data within the
_service dates_ associated with the start and end dates, which are
_calendar dates_. For example, if _2019-01-01_ is supplied as the start
and end date, data from the previous service date that took place in the
current calendar date will **not** be collected, while data belonging to
the current service date that took place in the following calendar date
will be collected.

#### From flagged_data.py

Using the `--select` argument enables the handling of database queries
from the command line. Listed below are the current types of queries
that the program supports.

##### `DataFrame query_flags_by_row_id(row_id, service_year, service_period)`

_row_id_: integer, id of the row to query. Currently, the program does not
provide a exclusive operation for seeking a particular row, you must already
know the id of the row you're looking for.

_service_year_: integer, four-digit calendar year

_service_period_: integer, three service periods per year, in-order [1, 2, 3]

Example usage: `main.py --select --row=57 --year=2019 --service_period=1`

This queries the database for all flags associated with the specified row.

##### `DataFrame query_flags_by_flag_id`

_flag_: string, the name of a flag

_limit_: integer, the numerical limit of rows to be returned

Example usage: `main.py --select --flag=duplicate --limit=50`

This queries the database for the most recent instances of rows that
received the specified flag. This query has an optional _limit_ parameter
that defines the maximum number of rows to be returned, with a default
value of 100 if the argument is not supplied. Data returned includes a
maximum of _limit_ row_ids.