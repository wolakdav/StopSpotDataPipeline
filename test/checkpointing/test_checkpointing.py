import pytest
import os
from src.checkpointing import Checkpoint

@pytest.fixture
def checkpoint(tmp_path):
    checkpoint = Checkpoint()
    checkpoint._file = tmp_path / "checkpoint.txt"  # Kinda gross but should make it easy to determine the output
    return checkpoint

# This test displays that if the checkpoint.txt file is not found while reading, todays date will be the range for
# the checkpointing system
def test_read_file_dne(checkpoint):
    exists = os.path.exists(checkpoint._file)
    if exists:
        print("checkpoint.txt deleted")
        os.remove("checkpoint.txt")  # Remove the file if it exists in the directory
    print(checkpoint.read_from_file())
    exists = os.path.exists(checkpoint._file)
    assert exists == True

# The intention of this test was to display firstly, the file will be created and written to
# and secondly that if the file already exists with contents it will overwrite them.
# If you want to verify run the test_read_file_dne and then this test and you will see the file is overwritten
def test_write_to_file(checkpoint):
    checkpoint.write_to_file("2019-03-01", "2019-03-07")
    print(checkpoint.read_from_file())
    exists = os.path.exists(checkpoint._file)
    assert exists == True
