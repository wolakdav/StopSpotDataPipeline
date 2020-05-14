from flaggers.flagger import flaggers, Flags
import pytest
import pandas
import numpy as np

class DataRow():
    def __init__(self):
        self.row_id = "good"
        self.service_date = "good"
        self.vehicle_number = "good"
        self.leave_time = "good"
        self.train = "good"
        self.route_number = "good"
        self.direction = "good"
        self.service_key = "good"
        self.trip_number = "good"
        self.stop_time = np.nan
        self.arrive_time = "good"
        self.dwell = "good"
        self.location_id = "good"
        self.door = "good"
        self.ons = "good"
        self.offs = "good"
        self.estimated_load = "good"
        self.lift = "good"
        self.maximum_speed = None
        self.train_mileage = "good"
        self.pattern_distance = "good"
        self.location_distance = "good"
        self.x_coordinate = "good"
        self.y_coordinate = "good"
        self.data_source = "good"
        self.schedule_status = "good"
        self.trip_id = "good"

@pytest.fixture
def duplicate_flagger():
    return [f for f in flaggers if f.name == 'Duplicate'][0]

@pytest.fixture
def no_duplications():
    full_list = []
    full_list.append(vars(DataRow()))
    return pandas.DataFrame(full_list)

@pytest.fixture
def duplications():
    full_list = []
    full_list.append(vars(DataRow()))
    full_list.append(vars(DataRow()))
    return pandas.DataFrame(full_list)


# There are duplicates returned.
def test_duplicate_flagger_happy(duplicate_flagger, duplications):
    result = duplicate_flagger.flag(duplications, "config")
    assert not result.empty and 'service_date' in result

# There are no duplicates returned.
def test_duplicate_flagger_sad(duplicate_flagger, no_duplications):
    result = duplicate_flagger.flag(no_duplications, "config")
    assert result.empty

# The ValueError is raised as the input DataFrame lacks the 'serivce_date'
# field.
def test_duplicate_flagger_bad(duplicate_flagger):
    with pytest.raises(ValueError):
        duplicate_flagger.flag(pandas.DataFrame(), "config")
