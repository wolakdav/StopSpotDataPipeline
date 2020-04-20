import datetime
import smtplib, ssl
from src.ios import IOs
from src.config import config

class _Notif(IOs):

    def __init__(self, config, verbose=True):
        super().__init__(verbose)
        self.msg = "A critical error has occured."
        self._port = 465  # For SSL
        self._config = config

    def print(self, string, obj=None, force=False):
        raise AttributeError("AttributeError: " + self.__class__.__name__ + " has no attribute 'print'")

    def prompt(self, prompt="", hide_input=False):
        raise AttributeError("AttributeError: " + self.__class__.__name__ + " has no attribute 'prompt'")

    #######################################################

    def email(self, subject="", msg=""):
        time = datetime.datetime.now()
        result = True
        if subject == "":
            subject = "Notification"

        if msg == "":
            msg = self.msg
        elif isinstance(msg, list):
            msg = "\n\n".join(msg)

        msg = "".join(["Subject: [StopSpot Pipeline] ", subject, " on/at ", str(time), "\n\n", msg])

        password = self._update_email_data()
        print(self.user_emails)
        if isinstance(self.user_emails, list):
            for user_email in self.user_emails:
                # Do not switch the order of this conditional expression,
                # Python will short circuit and not execute the method.
                result = self._email_user(user_email, msg, password) and result
        else:
            result = self._email_user(self.user_emails, msg, password)
        return result

    # This method will update self.user_emails and self.pipeline_email,
    # and it will password, as well as prompting for unavailable data.
    def _update_email_data(self):
        user_emails = self._config.get_value("user_emails")
        if user_emails is None:
            user_emails = self._prompt("Please enter the target email: ")
        self.user_emails = user_emails

        pipeline_email = self._config.get_value("pipeline_email")
        if pipeline_email is None:
            pipeline_email = self._prompt("Please enter this pipeline's email: ")
        self.pipeline_email = pipeline_email

        pipeline_email_passwd = self._config.get_value("pipeline_email_passwd")
        if pipeline_email_passwd is None:
            pipeline_email_passwd = self._prompt("Please enter this pipeline's email password: ", hide_input=True)

        return pipeline_email_passwd

    def _email_user(self, user_email, msg, password):
        self._print("TO:   ", user_email)
        self._print("FROM: ", self.pipeline_email)
        self._print(msg)

        try:
            context = ssl.create_default_context() # Create a secure SSL context
            #server = smtplib.SMTP_SSL("smtp.gmail.com", self._port, context=context)
            server = smtplib.SMTP_SSL("smtp.gmail.com", self._port, context=context)
            server.login(self.pipeline_email, password)
            server.sendmail(self.pipeline_email, user_email, msg)
        except smtplib.SMTPAuthenticationError:
            print("ERROR: email authentication failed.")
            return False
        except smtplib.SMTPException:
            print("ERROR: a general email error occured.")
            return False

        return True

    #######################################################

    def django(self, msg=""):
        time = datetime.datetime.now()
