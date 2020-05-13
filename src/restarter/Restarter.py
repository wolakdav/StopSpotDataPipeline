from datetime import datetime
import os
from time import sleep
from src.logger import logger
from src.logger import Severity
from src.notif import notif
import sys

class Restarter:
    def critical_error(self, err):
        logger.start()
        now = datetime.now().strftime("%b %d %Y %H:%M:%S")

        msg = "An unexpected critical error occured while running the pipeline on {0}.\n\nThe contents of the error are listed below:\n\n{1} \n\nThe error has been logged and the pipeline will be restarted unless the retry limit has been reached. ".format(now, err)
        subject = "Pipeline Error - {0}".format(now)

        logger.log(msg, Severity.ERROR)
        logger.log(err, Severity.ERROR)
        notif.email(subject, msg)

        #this is needed because Docker will not restart a container that has been running for less than 10 seconds
        sleep(10)
        
        #Docker will only restart containers where the running process exits with a non-zero error code
        sys.exit(2)

