import datetime

class _Notif:
    def __init__(self, config):
        self.msg = "A critial error has occured."
        self._config = config
        # TODO: do something to check that the data exists
        # like make sure load is called / has data.

    def email(self, msg=""):
        time = datetime.datetime.now()

    def django(self, msg=""):
        time = datetime.datetime.now()

