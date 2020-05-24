# Disconnect the logging functionality from the main log file.
from src.ios import ios
# As tempting as it is to set this to /dev/null, that does not work.
ios._filename = "./test/.test_log.txt"
ios.start()
