import datetime
import smtplib, ssl
from ..ios import ios
from src.config import config
import os

class _Notif():

    def __init__(self, config):
        self._ios = ios
        self.msg = "A critical error has occured."
        self._port = 465  # For SSL
        self._config = config

        self.pipeline_email = ""  #tests fail without including this in the constructor

    #######################################################

    def email(self, subject="", msg=""):
        self._ios.log_and_print("Sending out an email to the user(s).")
        time = datetime.datetime.now()
        result = True
        if subject == "":
            subject = "Notification"

        msg = self._create_message(msg)
        msg = "".join(["Subject: [StopSpot Pipeline] ", subject, " on/at ", str(time), "\n\n", msg])

        password = self._update_email_data()
        self._ios.log_and_print(self.user_emails)
        if isinstance(self.user_emails, list):
            for user_email in self.user_emails:
                # Do not switch the order of this conditional expression,
                # Python will short circuit and not execute the method.
                result = self._email_user(user_email, msg, password) and result
        else:
            result = self._email_user(self.user_emails, msg, password)
        return result

    def _update_email_data(self):
        self.user_emails = self._get_config_value("user_emails", "Please enter the target email: ")
        self.pipeline_email = self._get_config_value("pipeline_email", "Please enter this pipeline's email: ")
        return self._get_config_value("pipeline_email_passwd", "Please enter this pipeline's email password: ", True)

    def _email_user(self, user_email, msg, password):
        self._ios.log_and_print("TO:   " + user_email)
        self._ios.log_and_print("FROM: " + self.pipeline_email)
        self._ios.log_and_print(msg)

        try:
            context = ssl.create_default_context() # Create a secure SSL context
            #server = smtplib.SMTP_SSL("smtp.gmail.com", self._port, context=context)
            server = smtplib.SMTP_SSL("smtp.gmail.com", self._port, context=context)
            server.login(self.pipeline_email, password)
            server.sendmail(self.pipeline_email, user_email, msg)
        except smtplib.SMTPAuthenticationError:
            self._ios.log_and_print(
                "Email authentication failed.", self._ios.Severity.ERROR)
            return False
        except smtplib.SMTPException:
            self._ios.log_and_print(
                "A general email error occured.", self._ios.Severity.ERROR)
            return False

        return True

    #######################################################

    def django(self, msg):
        '''
        Function responsible to outputting notification to a specific file (default: output/notif.txt, found in assets/config.json)

        Args: 
            msg (Object): Message to be written to a notif.tt file [Can be a list of messages]
        Yields: 
            notif.txt: file which contains notification message(s)

        Returns: 
            (Boolean): successful write: True, unsuccessful write: False
        '''

        time = datetime.datetime.now()
        msg = self._create_message(msg)
        filePath = self._get_config_value("notif_django_path", "Please enter this pipeline's django notification path: ", False)

        try:
            f = open(filePath, 'w')
            f.write(msg)
            f.close()
            return True
        except IOError: return False

    #######################################################
    '''Helper Functions'''
    #######################################################

    def _create_message(self, msg):
        '''
        Helper function which returns a message that will be used as a notification

        Args:
            msg (String|List): Notification message (can be empty String, normal String, or List of Strings)
        Returns: 
            msg (String): message that will be seen by the user as a notification
        '''

        #Case 1: One empty notification was passed: use default notification
        if msg == " ": msg = self.msg
        #Case 2: List of notification was passed: join together to create combined string
        elif isinstance(msg, list): msg = "\n\n".join(msg)

        return msg

    def _get_config_value(self, key, promptText, hidePromptInput=False):
        '''
        Helper function that returns a particular config value. Makes sure to return a valid value, my promting user if config
        value doesn't exist, or there is any problem with it

        Args: 
            key (String): config key (must be in assets/config.json), value if which is returned
            promptText (String): in case value is None, prompt user to enter value
            hidePromptInput (Boolean): specifies whether text typed by user in the prompt will be displayed

        Returns: 
            value (String): value for config key
        '''

        value = self._config.get_value(key)
        if value is None:
            value = self._ios._prompt(promptText, hidePromptInput)

        return value