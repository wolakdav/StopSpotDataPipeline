import datetime
import smtplib, ssl
from src.ios import IOs
from src.config import config

class _Notif(IOs):

    def __init__(self, config):
        super().__init__(True)
        self.msg = "A critial error has occured."
        self._port = 465  # For SSL
        self._config = config

    def print(self, string, obj=None, force=False):
        raise AttributeError("AttributeError: " + self.__class__.__name__ + " has no attribute 'print'")

    def prompt(self, prompt="", hide_input=False):
        raise AttributeError("AttributeError: " + self.__class__.__name__ + " has no attribute 'prompt'")

    #######################################################

    def email(self, msg=""):
        password = self._update_email_data()
        time = datetime.datetime.now()

        # TODO: Update this to use self._config, and update it in general.
        sender_email = "stopspot.noreply@gmail.com" # this needs sto be set up externally
        receiver_email = ""

        # Create a secure SSL context
        context = ssl.create_default_context()

        # TODO: catch smtplib exceptions
        with smtplib.SMTP_SSL("smtp.gmail.com", self._port, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, msg)

    # This method will update self.sender_email and
    # self.pipeline_email, and it will password, as well as prompting for
    # unavailable data.
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
            pipeline_email_passwd = self._prompt("Please enter this pipeline's email: ")

        return pipeline_email_passwd

    #######################################################

    def django(self, msg=""):
        time = datetime.datetime.now()
