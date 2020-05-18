'''
Please note, for successfull passing of this test, assets/ete_config.json must be correctly set [see docs/ete-test.md for details]
'''

import pytest
from src.tables import CTran_Data
from src.tables import Flags
from src.tables import Flagged_Data
from datetime import datetime
import json

from src.tables import CTran_Data
from src.tables import Flagged_Data
from src.tables import Flags
from src.tables import Service_Periods

from src.client import _Client
from src.config import Config

#############################################################################################################
#FAKE CLASSES###################################################################################FAKE CLASSES#
#***********************************************************************************************************#

#Returns fake config instance
@pytest.fixture()
def fake_config():
	class Fake_Config(Config):
		def __init__(self):
			self._data = {}

		def load(self):
			self._filename = "./assets/ete_config.json"

			try:
				with open(self._filename) as f:
					self._data = json.load(f)
			except (FileNotFoundError, ValueError):
				return False

			return True


	return Fake_Config()

#Returns fake client instance
@pytest.fixture
def fake_client(fake_config):
	class Fake_Client(_Client):
		def __init__(self, verbose=True):
			self.verbose = verbose

			self.config = fake_config
			self.config.load()

			self._output_path = self.config.get_value("output_path")
			self._output_type = self.config.get_value("output_type")

			portal_user = self.config.get_value("portal_user")
			portal_passwd = self.config.get_value("portal_passwd")
			portal_hostname = self.config.get_value("portal_hostname")
			portal_db_name = self.config.get_value("portal_db_name")
			portal_schema = self.config.get_value("portal_schema")
			if portal_user and portal_passwd and portal_hostname and portal_db_name and portal_schema:
				self.ctran = CTran_Data(portal_user, portal_passwd, portal_hostname, portal_db_name, portal_schema, verbose=verbose)

			pipe_user = self.config.get_value("pipeline_user")
			pipe_passwd = self.config.get_value("pipeline_passwd")
			pipe_hostname = self.config.get_value("pipeline_hostname")
			pipe_db_name = self.config.get_value("pipeline_db_name")
			pipe_schema = self.config.get_value("pipeline_schema")
			if pipe_user and pipe_passwd and pipe_hostname and pipe_db_name and pipe_schema:
				self.flagged = Flagged_Data(pipe_user, pipe_passwd, pipe_hostname, pipe_db_name, pipe_schema, verbose=verbose)


			self.flags = Flags(pipe_user, pipe_passwd, pipe_hostname, pipe_db_name, pipe_schema, verbose=verbose)
			self.service_periods = Service_Periods(pipe_user, pipe_passwd, pipe_hostname, pipe_db_name, pipe_schema, verbose=verbose)

	return Fake_Client()

#############################################################################################################
#INSTANCE FIXTURES#########################################################################INSTANCE_FIXTURES#
#***********************************************************************************************************#

#Returns client instance: contains other initialized instances
@pytest.fixture
def client(fake_client):
	client = fake_client
	return client

#Returns ctran instance
@pytest.fixture
def ctran(client):
	return client.ctran

#Returns flagged instance
@pytest.fixture
def flagged(client):
	return client.flagged

#Returns flags instance
@pytest.fixture
def flags(client):
	return client.flags

#***********************************************************************************************************#
#CREATION, PROCESSING, AND REMOVAL##########################################CREATION, PROCESSING AND REMOVAL#
#***********************************************************************************************************#

#Helper function that loads data into test aperture: should return True on success
@pytest.fixture
def save_ctran_test_data(ctran):
	if ctran != None: 
		return ctran.create_table(ctran_sample_name = "/ctran_ete_test.csv")
	else: return False 

#Helper function that returns number of rows in input data
@pytest.fixture
def get_ctran_test_data(ctran):
	if ctran != None:
		#return ctran.get_full_table()
		start = datetime(1900, 1, 1)
		end = datetime(2100, 1, 1)
		return ctran.query_date_range(start, end)
	else: return False

#Helper function that creates hive [schema and tables for output]: should return True on success
@pytest.fixture
def create_hive(client):
	try:
		client.create_hive()
	except:
		return False

	return True

#Helper function that processes and saves output to hive: Should return True on success
@pytest.fixture
def process_and_save(client):
	start = datetime(1900, 1, 1)
	end = datetime(2100, 1, 1)
	return client.process_data(start, end)

#Helper function that removes aperture: where input information resides
@pytest.fixture
def remove_input_information(ctran):
	return ctran.delete_schema()

#Helper function that removes hive: where output information resides
@pytest.fixture
def remove_output_information(flagged):
	return flagged.delete_schema()

#***********************************************************************************************************#
#OUTPUT DATA#####################################################################################OUTPUT DATA#
#***********************************************************************************************************#

#Returns processed data (flagged table)
@pytest.fixture
def flagged_data(flagged):
	return flagged.get_full_table()

@pytest.fixture
def flags_data(flags):
	return flags.get_full_table()

#***********************************************************************************************************#
#HELPER TESTS###################################################################################HELPER TESTS#
#############################################################################################################

#Tests valid client instance creation
def test_client(client):
	assert isinstance(client, _Client)

#Test valid ctran instance creation
def test_ctran(ctran):
	assert isinstance(ctran, CTran_Data)

#Test valid flagged instance creation
def test_flagged(flagged):
	assert isinstance(flagged, Flagged_Data)

#Test valid flags instance creation
def test_flags(flags):
	assert isinstance(flags, Flags)

#Tests saving test data to aperture
def test_save_ctran_test_data(save_ctran_test_data):
	assert save_ctran_test_data == True

#Test hive creation, for output/processed data
def test_create_hive(create_hive):
	assert create_hive == True

#Tests data processing and saving [function in client]
def test_process_and_save(process_and_save):
	assert process_and_save == True

#Test that correct number of rows has been inserted
def test_pull_test_data(get_ctran_test_data):
	assert not type(get_ctran_test_data) is None
	assert len(get_ctran_test_data) == 5

#Tests pulling processed data for further testing
def test_pull_flagged_data(flagged_data):
	assert not type(flagged_data) is bool
	assert len(flagged_data) > 0

#Test pulling flags data
def test_pull_flags(flags_data):
	assert not type(flags_data) is bool
	assert len(flags_data) > 0

#***********************************************************************************************************#
#ACTUAL TESTS###################################################################################ACTUAL TESTS#
#############################################################################################################

#Test first (input) row: contains all None's, except date.
#Row_id can't be null because it's automatically incremented
def test_row_1(flagged_data, flags_data):
	#Step 1: Need to split flags to have only _NULL flags
	mask = flags_data.description.str.contains("_NULL")
	null_flags = flags_data[mask]

	#Should have exactly 27 NULL flags
	assert len(null_flags) == 27

	#Step 2: Need to split flagged to contain data for Row 1 only 
	mask = flagged_data.row_id == 1
	first_row = flagged_data[mask]

	#Should have 25 NULL flags: service_date can't be null (won't be flagged), and row_id is inserted automatically (can't be null)
	assert len(first_row) == 25

	#Step 3: Iterate over null flags omiting service_date
	for index, row in null_flags.iterrows():
		if not ((row["description"] == "SERVICE_DATE_NULL") or (row["description"] == "ROW_ID_NULL")):
			#for each null_flag that we want to check: check if first row contains it (must contain all null flags except 3 above)
			assert any(first_row["flag_id"] == row["flag_id"]) == True

#Test second (input) row: all data is good, except there is data for unobserved_stop flag to be turned on
def test_row_2(flagged_data, flags_data):
	#Step 1: Need to split flags to have only UNOBSERVED_STOP flag
	mask = flags_data.description.str.contains("UNOBSERVED_STOP")
	unobserved_flag_row = flags_data[mask]
	unobserved_flag = unobserved_flag_row["flag_id"].values[0]

	#Must only have 1 row
	assert len(unobserved_flag_row) == 1

	#Step 2: Only need data for 2nd row
	mask = flagged_data.row_id == 2
	second_row = flagged_data[mask]
	second_row_flag = second_row["flag_id"].values[0]

	#Must only have 1 row
	assert len(second_row) == 1

	#Step 3: Confirm flag is turned on
	assert unobserved_flag == second_row_flag

#Test third (input) row: all data is good, except there is data for unopened_door flag to be turned on
def test_row_3(flagged_data, flags_data):
	#Step 1: Need to split flags to have only UNOBSERVED_STOP flag
	mask = flags_data.description.str.contains("UNOPENED_DOOR")
	unopened_door_flag_row = flags_data[mask]
	unopened_door_flag = unopened_door_flag_row["flag_id"].values[0]

	#Must only have 1 row
	assert len(unopened_door_flag_row) == 1

	#Step 2: Only need data for 3rd row
	mask = flagged_data.row_id == 3
	third_row = flagged_data[mask]
	third_row_flag = third_row["flag_id"].values[0]

	#Must only have 1 row
	assert len(third_row) == 1

	#Step 3: Confirm flag is turned on
	assert unopened_door_flag == third_row_flag

#Test fourth and fifth (rows): all data is good, but they're duplicates of each other, therefore both must contain duplicate flag
def test_row_4_and_5(flagged_data, flags_data):
	#Step 1: Need to split flags to have only UNOBSERVED_STOP flag
	mask = flags_data.description.str.contains("DUPLICATE")
	duplicate_flag_row = flags_data[mask]
	duplicate_flag = duplicate_flag_row["flag_id"].values[0]

	#Must only have 1 row
	assert len(duplicate_flag_row) == 1

	#Step 2: Only need data for 4th and 5th rows
	mask = flagged_data.row_id == 4
	fourth_row = flagged_data[mask]
	fourth_row_flag = fourth_row["flag_id"].values[0]

	mask = flagged_data.row_id == 5
	fifth_row = flagged_data[mask]
	fifth_row_flag = fifth_row["flag_id"].values[0]

	#Must only have 1 row for each input row
	assert len(fourth_row) == 1
	assert len(fifth_row) == 1

	#Step 3: Confirm flag is turned on
	assert duplicate_flag == fourth_row_flag
	assert duplicate_flag == fifth_row_flag

#Test sixth row: All data is good, but service_date is null, therefore data will not be flagged, and thus absent from flagged_data: thus row_id = 5 will not be in the table
def test_row_6(flagged_data):
	mask = flagged_data.row_id == 6
	sixth_row = flagged_data[mask]
	assert len(sixth_row) == 0

#***********************************************************************************************************#
#RECYCLE#############################################################################################RECYCLE#
#############################################################################################################

#Test successful aperture removal: where input information resides
def test_input_information_removal(ctran, remove_input_information):
	#Step 1: Assert successful removal
	assert remove_input_information == True

	#Step 2: Try to access table: should return None
	start_date = datetime(1900, 1, 1)
	end_date = datetime(2100, 1, 1)
	assert ctran.query_date_range(start_date, end_date) == None

#Test successful hive removal: where output information resides
def test_output_information_removal(remove_output_information, flagged_data):
	#Step 1: Assert succesful removal
	assert remove_output_information == True

	#Step 2: Try to access table: should return False
	assert flagged_data == None
