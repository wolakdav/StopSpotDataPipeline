#TODO: Need to assert each step, because its a pipeliend approcach: uploading stuff, getting it, running analyzers etc

import pytest
import os
from src.tables import CTran_Data
from src.config import config
from datetime import datetime

#Returns instance of cTran
@pytest.fixture
def instance():
    ctran = None
    
    config.load(read_env_data = False)

    user = config.get_value('pipeline_user')
    passwd = config.get_value('pipeline_passwd')
    hostname = config.get_value('pipeline_hostname')
    db_name = config.get_value('pipeline_db_name')
    db_schema = config.get_value('portal_schema')

    if user and passwd and hostname and db_name:
        ctran = CTran_Data(user, passwd, hostname, db_name, db_schema, verbose=True)
    
    return ctran

#Helper function that loads data into test aperture
@pytest.fixture
def save_test_data(instance):
	if instance != None: 
		return instance.create_table(ctran_sample_name = "/ctran_ete_test.csv", exists_action="replace")
	else: return False 

#Helper function that fetches test data from test aperture
@pytest.fixture
def pull_test_data(instance):
	start = datetime(2019, 1, 1)
	end = datetime(2020, 5, 6)
	return instance.query_date_range(date_from=start, date_to=end)

#Helper function that runs analyzers and returns analyzed data that will be saved
@pytest.fixture
def run_analyzers(pull_test_data):
	flagged_rows = []

    for row_id, row in ctran_df.iterrows():
        month = row.service_date.month
        year = row.service_date.year
        service_key = service_periods.query_or_insert(month, year)

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
'''

#Helper function that saves analyzed data
@pytest.fixture()
def save_analyzed_data():

#Helper function that pulls analyzed data from hive
@pytest.fixture
def pull_analyzed_data():
'''

'''
def test_saving_data(save_test_data):
	assert save_test_data == True
	#assert instance != None

def test_pulling_data(pull_test_data):
	invalid_data_returned = isinstance(None, type(pull_test_data))
	assert not invalid_data_returned
	if not invalid_data_returned: assert pull_test_data.shape[0] > 0
'''
	