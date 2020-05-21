import getpass
from .logger import Logger
from .logger import Severity

class IOs(Logger):
    def __init__(self, filename=None):
        super().__init__()
        self._filename = filename
        self._started = False

    def __del__(self):
        self.stop()

    def prompt(self, prompt="", hide_input=False):
        return self._prompt(prompt, hide_input)

    def _prompt(self, prompt="", hide_input=False):
        while True:
            try:
                value = None
                if hide_input:
                    value = getpass.getpass(prompt)
                else:
                    value = input(prompt)
                return value
            except EOFError:
                print()

    def print(self, string, obj=None):
        return self._print(string, obj)

    def _print(self, string, obj=None):
        if obj is None:
            print(string)

        else:
            print(string, end="")
            print(obj)

    def log(self, message, severity=Severity.INFO):
        if not self._started:
            if self._filename is None:
                self.start()
            else:
                self.start(self._filename)
            self._started = True

        return super().log(message, severity)

    def stop(self):
        if self._started:
            super().stop()
            self._started = False

    def log_and_print(self, message, severity=Severity.INFO, obj=None):
        msg = self.log(message, severity)
        self.print(msg, obj)
        return msg
