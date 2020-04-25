import sys
from datetime import datetime

class Checkpoint:
    def __init__(self):
        self._file = "checkpoint.txt"

    # This function will write to the checkpoint file
    # if there is an existing checkpoint it will overwrite that checkpoint
    def write_to_file(self, date_to_checkpoint):
        f = open(self._file, "w")  # Will create the file if it does not exists, if it does it overwrites
        f.write(date_to_checkpoint.strftime("%Y-%m-%d"))
        f.close()
        return None

    # This function will read from the checkpoint file, it will get the last date that was checkpointed
    def read_from_file(self):
        f = open(self._file, "r")
        checkpoint_date = datetime.strptime(f.read(), "%Y-%m-%d")
        return checkpoint_date  # returns a datetime object

    # This function will save a new checkpoint to the checkpoint file
    # it will remove the current checkpoint and replace it
    def save_new_checkpoint(self, new_checkpoint):
        self.write_to_file(new_checkpoint)
        return None

    # This function will rerun to enter all the data from the checkpoint date to the current date
    def rerun_from_checkpoint(self):
        checkpoint_date = self.read_from_file()
        # Need to figure out what function we need to call to rerun the stuffz
        return None