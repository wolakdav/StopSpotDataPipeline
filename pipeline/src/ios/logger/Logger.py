import datetime
import os
from enum import Enum
from datetime import date

# NOTE: if you change this Enum, please adjust ios.md
class Severity(Enum):
    DEBUG = 1
    INFO = 2
    WARNING = 3
    ERROR = 4


class Logger:
    def __init__(self):
        self.Severity = Severity

    def start(self, filename='output/' + date.today().strftime('%Y-%m-%d') + '.txt'):
        self._f = open(filename,'a+')

    def log(self, message, severity=Severity.INFO):
        timestamp = datetime.datetime.now()
        tag = ''

        if severity == Severity.ERROR:
            tag = '[ERROR]'
        elif severity == Severity.INFO:
            tag = '[INFO]'
        elif severity == Severity.WARNING:
            tag = '[WARNING]'
        elif severity == Severity.DEBUG:
            tag = '[DEBUG]'

        self._f.write('{} ({}):   {}\n'.format(tag, timestamp, message))
        self._f.flush()
        os.fsync(self._f)

        if severity == Severity.INFO:
            return message
        else:
            return '{}: {}'.format(tag, message)

    def stop(self):
        self.log('The logger is shutting down.', self.Severity.INFO)
        self._f.close()
