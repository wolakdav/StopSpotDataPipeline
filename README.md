# TeamBeeCapstoneProject

Repository for Portland State University Winter-Spring Team Bees capstone project.

## Setup

These are Linux instructions. It is recommended to adjust `assets/config.json`
as appropriate (for more, see below).

### Install and Activate Python Dependencies

1) `python3 -m pip install --user pipenv`: Install pipenv locally - Python 3.7 is required.
2) `cd TeamBeeCapstoneProject`
3) `pipenv shell`: Activate the virtual environment.
4) `pipenv install`: Install the dependencies specified by `Pipfile.lock` and `Pipefile.`
5) `exit`: Close the virtual environment.

### First Time Execution

If the output database has not been generated or used, then it is required to
first boot the CLI menu to build the output database's schema, and then
manually execute this program. This is possible via the same CLI menu or via
the command arguments (for more, see below).

## General Usage

1) `pipenv shell`: Activate the virtual environment.
2) Executing the program.  
  a. `python3 main.py`: Start the program's CLI menu.  
  b. `python3 main.py --help`: See the instructions for use as a command.  
3) `exit`: Close the virtual environment.

Alternatively, place the below into the system's crontab to automatically process new data every 24 hours.
Again, this does require the First Time Execution to have already occurred.  
`TODO: place the crontab line here.`

## Adjusting and Utilizing Endpoints

#### `assets/config.json`

This configuration file controls various data about the Pipeline. Some notable
settings controlled here are as follows.

1) `user_emails`: The list of email(s) to send critical error messages to.
2) `pipeline_email_passwd`: The password to the Pipeline's email, used for
critical email notifications. For obvious reasons, this is not supplied by default.
3) `pipeline_user`: The username for the Pipeline to use to access the output database.
4) `pipeline_passwd`: The password for the Pipeline to use to access the output database.
5) `pipeline_hostname`: The hostname for the Pipeline to use to access the output database.
6) `pipeline_db_name`: The database name for the Pipeline to use to access the output database.
7) `notif_django_path`: The output of the Django file (see `output/notif.txt` for more).

For more, see `docs/config_readme.md`.

#### `bin/env_data.sh`

This file is an alternate way to set the relevant output database data by
configuring environment variables. These environment variables will take
priority over the data in `assets/config.json`.

For more, see `docs/env_data.md`.

### `output/`

##### `output/log.txt`

This is the general purpose log file.

##### `output/notif.txt`

This is the default output location for critical error messages capable of
being picked-up by a Django application.
