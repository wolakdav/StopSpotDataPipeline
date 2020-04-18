import datetime
import smtplib, ssl
from src.ios import IOs
from src.config import config

class _Notif(IOs):

    def __init__(self, config):
        self.msg = "A critial error has occured."
        self._config = config

    #######################################################

    def email(self, msg=""):
        password = self._update_email_data()
        time = datetime.datetime.now()

        # TODO: Update this to use self._config, and update it in general.
        port = 465  # For SSL
        sender_email = "stopspot.noreply@gmail.com" # this needs sto be set up externally
        receiver_email = ""

        # Create a secure SSL context
        context = ssl.create_default_context()

        with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, msg)

    # TODO: this method will update self.port, self.sender_email, and
    # self.receiver_email, and it will return None on failure and the password
    # on success.
    def _update_email_data(self):
        # TODO: this method needs to make sure that the data is actually in
        # config, and if it isn't prompt via IOs for it.
        pass

    #######################################################

    def django(self, msg=""):
        time = datetime.datetime.now()
