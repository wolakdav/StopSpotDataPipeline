import getpass
from ..logger import Logger

class IOs(Logger):
    def __init__(self):
        self.start()

    def __del__(self):
        # In case the user fails to close the logger explicitly, this will stop
        # it eventually. This will not thrown an error if a closed file is
        # closed again. This is fine because Logger.log() will flush each log
        # as it goes.
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

    def log_and_print(self, message, severity, obj=None):
        self._print(self.log(message, severity), obj)
