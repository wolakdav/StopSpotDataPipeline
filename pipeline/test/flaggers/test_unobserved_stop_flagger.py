from flaggers.flagger import flaggers, Flags
from src.config import config
import pytest

class GoodData():
	def __init__(self):
		self.location_distance = 0

class BadData():
	def __init__(self):
		#location_distance should be set from .env, but currently check unopenedDoor.py for value: 50
		self.location_distance = 666

@pytest.fixture
def unobserved_stop_flagger():
  return [f for f in flaggers if f.name == 'Unobserved Stop'][0]

@pytest.fixture
def config_instance():
	config.load(read_env_data=True)
	return config

@pytest.fixture
def good_data():
	return vars(GoodData())

@pytest.fixture
def bad_data():
	return vars(BadData())

#Should NOT return a flags, since data is good [returns empty list]
def test_unobserved_stop_flagger_on_good_data(unobserved_stop_flagger, good_data, config_instance):
	flags = unobserved_stop_flagger.flag(good_data, config_instance)
	assert len(flags) == 0

#Should return flags, since data is bad [returns list with 1 flag]
def test_unobserved_stop_flagger_on_bad_data(unobserved_stop_flagger, bad_data, config_instance):
	flags = unobserved_stop_flagger.flag(bad_data, config_instance)
	assert len(flags) == 1
	assert Flags.UNOBSERVED_STOP in flags

