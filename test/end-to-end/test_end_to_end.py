#TODO: Need to assert each step, because its a pipeliend approcach: uploading stuff, getting it, running analyzers etc

import pytest
import os
from src.tables import CTran_Data
from src.tables import Flagged_Data
from src.tables import Service_Periods
from src.config import config
from datetime import datetime
from flaggers.flagger import flaggers

from src import client_instance

#Config instance is used couple of times, therefore need a separate fixture for it
@pytest.fixture
def config_instance():
	config.load(read_env_data = False)
	return config

#Returns instance of cTran
@pytest.fixture
def ctran_instance(config_instance):
	ctran = None

	portal_user = config_instance.get_value("portal_user")
	portal_passwd = config_instance.get_value("portal_passwd")
	portal_hostname = config_instance.get_value("portal_hostname")
	portal_db_name = config_instance.get_value("portal_db_name")
	portal_schema = config_instance.get_value("portal_schema")
	if portal_user and portal_passwd and portal_hostname and portal_db_name :
		if portal_schema:
			ctran = CTran_Data(portal_user, portal_passwd, portal_hostname, portal_db_name, portal_schema, verbose=True)
		else:
			ctran = CTran_Data(portal_user, portal_passwd, portal_hostname, portal_db_name, verbose=True)

	return ctran

@pytest.fixture
def flagged_instance(config_instance):
	flagged = None

	pipe_user = config_instance.get_value("pipeline_user")
	pipe_passwd = config_instance.get_value("pipeline_passwd")
	pipe_hostname = config_instance.get_value("pipeline_hostname")
	pipe_db_name = config_instance.get_value("pipeline_db_name")
	pipe_schema = config_instance.get_value("pipeline_schema")
	if pipe_user and pipe_passwd and pipe_hostname and pipe_db_name:
		if pipe_schema:
			flagged = Flagged_Data(pipe_user, pipe_passwd, pipe_hostname, pipe_db_name, pipe_schema, verbose=True)
		else:
			flagged = Flagged_Data(pipe_user, pipe_passwd, pipe_hostname, pipe_db_name, verbose=True)

	return flagged

@pytest.fixture
def service_period_instance(flagged_instance):
	service_periods = Service_Periods(verbose=True, engine=flagged_instance.get_engine().url)
	return service_periods

#Helper function that loads data into test aperture
@pytest.fixture
def save_ctran_test_data(ctran_instance):
	if ctran_instance != None: 
		return ctran_instance.create_table(ctran_sample_name = "/ctran_ete_test.csv", exists_action="replace")
	else: return False 

#Helper function that fetches test data from test aperture
@pytest.fixture
def get_ctran_test_data(ctran_instance):
	start = datetime(2019, 1, 1)
	end = datetime(2020, 5, 6)
	return ctran_instance.query_date_range(date_from=start, date_to=end)

#Helper function that runs analyzers and returns analyzed data that will be saved
@pytest.fixture
def get_analyzed_data(get_ctran_test_data, service_period_instance):
	flagged_rows = []
	ctran_df = get_ctran_test_data

	if ctran_df is None:
		return False

	for row_id, row in ctran_df.iterrows():
		month = row.service_date.month
		year = row.service_date.year
		service_key = service_period_instance.query_or_insert(month, year)

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


		date = row["service_date"]
		date = "".join([str(date.year), "/", str(date.month), "/", str(date.day)])
		for flag in flags:
			flagged_rows.append([
				row_id,
				service_key,
				int(flag),
				date
			])

	#flagged_instance.write_table(flagged_rows)
	return flagged_rows

@pytest.fixture
def save_analyzed_data(flagged_instance, get_analyzed_data):
	return flagged_instance.write_table(get_analyzed_data)

@pytest.fixture
def client():
	return client_instance

@pytest.fixture
def tst(client):
	start = datetime(2019, 1, 1)
	end = datetime(2020, 5, 6)
	return client.process_data(start, end)


def test_tst(tst):
	assert tst == True


'''
def test_saving_data(save_ctran_test_data):
	assert save_ctran_test_data == True
'''

'''
def test_pulling_data(get_ctran_test_data):
	invalid_data_returned = isinstance(None, type(get_ctran_test_data))
	assert not invalid_data_returned
	if not invalid_data_returned: assert get_ctran_test_data.shape[0] > 0
'''
'''
def test_analyzing(get_analyzed_data):
	invalid_data_returned = type(get_analyzed_data) is bool
	assert not invalid_data_returned
	if not invalid_data_returned: assert len(get_analyzed_data) > 0
'''

#def test_save_analyzed_data(save_analyzed_data):
	#assert save_analyzed_data == True

	