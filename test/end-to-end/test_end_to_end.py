'''
Please note, for successfull passing of this test, config.json must be correctly set [see docs/ete-testing.md for details]
'''

import pytest
from src.client import _Client
from src.tables import CTran_Data
from src.tables import Flags
from src.tables import Flagged_Data
from datetime import datetime

#############################################################################################################
#INSTANCE FIXTURES#########################################################################INSTANCE_FIXTURES#
#***********************************************************************************************************#

#Returns client instance: contains other initialized instances
@pytest.fixture
def client():
    client = _Client(read_env_data=False)
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
#CREATION AND PROCESSING#############################################################CREATION AND PROCESSING#
#***********************************************************************************************************#

#Helper function that loads data into test aperture: should return True on success
@pytest.fixture
def save_ctran_test_data(ctran):
	if ctran != None: 
		return ctran.create_table(ctran_sample_name = "/ctran_ete_test.csv", exists_action="replace")
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

'''
#Test first (input) row: contains all None's, except date and trip_id, because without them there will be no input into flagged table
def test_row_1(flagged_data, flags_data):
	#Step 1: Need to split flags to have only _NULL flags
	mask = flags_data.description.str.contains("_NULL")
	null_flags = flags_data[mask]

	#Should have more than 1 NULL flag
	assert len(null_flags) > 1

	#Step 2: Need to split flagged to contain data for Row 1 only (counting starts from 0, so 0)
	mask = flagged_data.row_id == 0
	first_row = flagged_data[mask]

	#Should have more than flagged 1 row for first inout row
	assert len(first_row) > 1

	#Step 3: Iterate over null flags omiting row_id, service_date, and trip_id
	for index, row in null_flags.iterrows():
		if not ((row["description"] == "ROW_ID_NULL") or (row["description"] == "SERVICE_DATE_NULL")):
			#for each null_flag that we want to check: check if first row contains it (must contain all null flags except 3 above)
			assert any(first_row["flag_id"] == row["flag_id"]) == True
'''

'''
#Test second (input) row: all data is good, except there is data for unobserved_stop flag to be turned on
def test_row_2(flagged_data, flags_data):
	#Step 1: Need to split flags to have only UNOBSERVED_STOP flag
	mask = flags_data.description.str.contains("UNOBSERVED_STOP")
	unobserved_flag_row = flags_data[mask]
	unobserved_flag = unobserved_flag_row["flag_id"].values[0]

	#Must only have 1 row
	assert len(unobserved_flag_row) == 1

	#Step 2: Only need data for 2nd row
	mask = flagged_data.row_id == 1
	second_row = flagged_data[mask]
	second_row_flag = second_row["flag_id"].values[0]

	#Must only have 1 row
	assert len(second_row) == 1

	#Step 3: Confirm flag is turned on
	assert unobserved_flag == second_row_flag
'''
'''
#Test third (input) row: all data is good, except there is data for unopened_door flag to be turned on
def test_row_3(flagged_data, flags_data):
	#Step 1: Need to split flags to have only UNOBSERVED_STOP flag
	mask = flags_data.description.str.contains("UNOPENED_DOOR")
	unopened_door_flag_row = flags_data[mask]
	unopened_door_flag = unopened_door_flag_row["flag_id"].values[0]

	#Must only have 1 row
	assert len(unopened_door_flag_row) == 1

	#Step 2: Only need data for 3rd row
	mask = flagged_data.row_id == 2
	third_row = flagged_data[mask]
	third_row_flag = third_row["flag_id"].values[0]

	#Must only have 1 row
	assert len(third_row) == 1

	#Step 3: Confirm flag is turned on
	assert unopened_door_flag == third_row_flag
'''

'''
#Test fourth and fifth (rows): all data is good, but they're duplicates of each other, therefore both must contain duplicate flag
def test_row_4_and_5(flagged_data, flags_data):
	#Step 1: Need to split flags to have only UNOBSERVED_STOP flag
	mask = flags_data.description.str.contains("DUPLICATE")
	duplicate_flag_row = flags_data[mask]
	duplicate_flag = duplicate_flag_row["flag_id"].values[0]

	#Must only have 1 row
	assert len(duplicate_flag_row) == 1

	#Step 2: Only need data for 4th and 5th rows
	mask = flagged_data.row_id == 3
	fourth_row = flagged_data[mask]
	fourth_row_flag = fourth_row["flag_id"].values[0]

	mask = flagged_data.row_id == 4
	fifth_row = flagged_data[mask]
	fifth_row_flag = fifth_row["flag_id"].values[0]

	#Must only have 1 row for each input row
	assert len(fourth_row) == 1
	assert len(fifth_row) == 1

	#Step 3: Confirm flag is turned on
	assert duplicate_flag == fourth_row_flag
	assert duplicate_flag == fifth_row_flag
'''

#Test sixth row: All data is good, but service_date is null, therefore data will not be flagged, and thus absent from flagged_data: thus row_id = 5 will not be in the table
def test_row_6(flagged_data):
	mask = flagged_data.row_id == 5
	sixth_row = flagged_data[mask]
	assert len(sixth_row) == 0
#TODO: When date or trip id isn't present, no new row will be inserted into flagged, thus test for length of returned table when one or both is absent
