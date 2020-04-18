import datetime
import smtplib, ssl
from src.ios import IOs
from src.config import config

class _Notif(IOs):

    def __init__(self, config):
        super().__init__(True)
        self.msg = "A critical error has occured."
        self._port = 465  # For SSL
        self._config = config

    def print(self, string, obj=None, force=False):
        raise AttributeError("AttributeError: " + self.__class__.__name__ + " has no attribute 'print'")

    def prompt(self, prompt="", hide_input=False):
        raise AttributeError("AttributeError: " + self.__class__.__name__ + " has no attribute 'prompt'")

    #######################################################

    # msg can be a list of strs which will be joined on double new lines
    def email(self, subject="", msg=""):
        time = datetime.datetime.now()
        if subject == "":
            subject = "Notification"

        if msg == "":
            msg = self.msg
        elif isinstance(msg, list):
            msg = "\n\n".join(msg)

        msg = "".join(["Subject: [StopSpot Pipeline] ", subject, " on/at ", str(time), "\n\n", msg])

        password = self._update_email_data()
        self._print("TO:   ", self.user_email)
        self._print("FROM: ", self.pipeline_email)
        self._print(msg)

        try:
            context = ssl.create_default_context() # Create a secure SSL context
            server = smtplib.SMTP_SSL("smtp.gmail.com", self._port, context=context)
            server.login(self.pipeline_email, password)
            server.sendmail(self.pipeline_email, self.user_email, msg)
        except smtplib.SMTPAuthenticationError:
            print("ERROR: email authentication failed.")
            return False
        except smtplib.SMTPException:
            print("ERROR: a general email error occured.")
            return False

        return True

    # This method will update self.sender_email and
    # self.pipeline_email, and it will password, as well as prompting for
    # unavailable data.
    # TODO: add this comment to the doc
    # TODO: make the doc
    def _update_email_data(self):
        user_email = self._config.get_value("user_email")
        if user_email is None:
            user_email = self._prompt("Please enter the destination email: ")
        self.user_email = user_email

        pipeline_email = self._config.get_value("pipeline_email")
        if pipeline_email is None:
            pipeline_email = self._prompt("Please enter this pipeline's email: ")
        self.pipeline_email = pipeline_email

        pipeline_email_passwd = self._config.get_value("pipeline_email_passwd")
        if pipeline_email_passwd is None:
            pipeline_email_passwd = self._prompt("Please enter this pipeline's email password: ")

        return pipeline_email_passwd

    #######################################################

    def django(self, msg=""):
        time = datetime.datetime.now()
