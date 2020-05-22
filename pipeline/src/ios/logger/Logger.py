import datetime
import os
from enum import Enum
from datetime import date

class Severity(Enum):
    DEBUG = 1
    INFO = 2
    WARNING = 3
    ERROR = 4


class Logger:
    def __init__(self):
        self.Severity = Severity

    def start(self, filename='output/' + date.today().strftime('%m-%d-%Y') + '.txt'):
        self._f = open(filename,'a+')

    def log(self, message, severity=Severity.INFO):
        timestamp = datetime.datetime.now()
        msg = ''

        if severity == Severity.ERROR:
            msg = '[ERROR]  {}  {} \n'.format(timestamp, message)
        elif severity == Severity.INFO:
            msg = '[INFO]  {}  {} \n'.format(timestamp, message)
        elif severity == Severity.WARNING:
            msg = '[WARNING]  {}  {} \n'.format(timestamp, message)
        elif severity == Severity.DEBUG:
            msg = '[DEBUG]  {}  {} \n'.format(timestamp, message)

        self._f.write(msg)
        self._f.flush()
        os.fsync(self._f)
        return msg

    def stop(self):
        self.log('The logger is shutting down.', self.Severity.INFO)
        self._f.close()
