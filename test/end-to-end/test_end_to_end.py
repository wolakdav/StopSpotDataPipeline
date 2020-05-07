'''
Please note, for successfull passing of this test, config.json must be correctly set [see docs/ete-testing.md for details]
'''

import pytest
import os
from src.tables import CTran_Data
from src.tables import Flagged_Data
from src.tables import Service_Periods
from src.config import config
from datetime import datetime
from flaggers.flagger import flaggers

from src.client import _Client

#############################################################################################################

#Returns client instance: contains other initialized instances
@pytest.fixture
def client():
    client = _Client(read_env_data=False)
    return client

#Returns ctran instance
@pytest.fixture
def ctran(client):
	return client.ctran

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

@pytest.fixture
def processed_data(client):
	return client.flagged.get_full_table()

#############################################################################################################

#Tests valid client instance creation
def test_client(client):
	assert isinstance(client, _Client)

#Test valid ctran instance creation
def test_ctran(ctran):
	assert isinstance(ctran, CTran_Data)

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
def test_pull_processed_data(processed_data):
	assert not type(processed_data) is bool
	assert processed_data.shape[0] > 0
	