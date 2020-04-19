import io
import pytest
from src.notif import _Notif

@pytest.fixture
def mock_config():
    class Mock_Config:
        def __init__(self):
            self._data = {
                "user_email": "sw23@pdx.edu",
                "pipeline_email": "stopspot.noreply@gmail.com",
                "pipeline_email_passwd": "invalid"
            }

        def get_value(self, value):
            if value in self._data:
                return self._data[value]

    return Mock_Config()

@pytest.fixture
def instance_fixture(mock_config):
    return _Notif(mock_config)

@pytest.fixture
def custom_server():
    def create_server(expected_subject, expected_msg, expected_data):
        class Server:
            def __init__(self, string, port, context):
                assert string == "smtp.gmail.com"
                assert port == 465

            def login(self, sender_email, password):
                assert sender_email == expected_data["pipeline_email"]
                assert password == expected_data["pipeline_email_passwd"]

            def sendmail(self, sender_email, recipient_email, msg):
                assert sender_email == expected_data["pipeline_email"]
                assert recipient_email == expected_data["user_email"]
                assert expected_subject in msg
                assert "\n\n".join(expected_msg) in msg

        def create(string, port, context):
            return Server(string, port, context)

        return create

    return create_server

def test_constructor(mock_config):
    dummy = _Notif(mock_config, True)
    assert dummy.verbose == True
    assert dummy._config == mock_config
    assert isinstance(dummy.msg, str)
    with pytest.raises(AttributeError):
        assert dummy.user_email
        assert dummy.pipeline_email

def test_no_print(instance_fixture):
    with pytest.raises(AttributeError):
        assert instance_fixture.print("string")

def test_no_prompt(instance_fixture):
    with pytest.raises(AttributeError):
        assert instance_fixture.prompt("string")

def test_update_email_data_happy(instance_fixture):
    expected = instance_fixture._config._data
    assert instance_fixture._update_email_data() == expected["pipeline_email_passwd"]
    assert instance_fixture.user_email == expected["user_email"]
    assert instance_fixture.pipeline_email == expected["pipeline_email"]

def test_update_email_data_no_password(monkeypatch, instance_fixture):
    expected = instance_fixture._config._data.pop("pipeline_email_passwd") + "\n"
    monkeypatch.setattr("getpass.getpass", lambda _: expected)
    assert expected == instance_fixture._update_email_data()

    data = instance_fixture._config._data
    assert instance_fixture.user_email == data["user_email"]
    assert instance_fixture.pipeline_email == data["pipeline_email"]

def test_update_email_data_no_user_email(monkeypatch, instance_fixture):
    expected = instance_fixture._config._data.pop("user_email")
    monkeypatch.setattr("sys.stdin", io.StringIO(expected + "\n"))
    data = instance_fixture._config._data
    assert instance_fixture._update_email_data() == data["pipeline_email_passwd"]
    assert instance_fixture.user_email == expected
    assert instance_fixture.pipeline_email == data["pipeline_email"]

def test_update_email_data_no_pipeline_email(monkeypatch, instance_fixture):
    expected = instance_fixture._config._data.pop("pipeline_email")
    monkeypatch.setattr("sys.stdin", io.StringIO(expected + "\n"))
    data = instance_fixture._config._data
    assert instance_fixture._update_email_data() == data["pipeline_email_passwd"]
    assert instance_fixture.user_email == data["user_email"]
    assert instance_fixture.pipeline_email == expected

def test_email_happy(monkeypatch, custom_server, instance_fixture):
    expected_subject = "This is a test"
    expected_msg = ["Hello,", "I am contacting you to perform a test.", "Best,", "Me"]
    expected_data = instance_fixture._config._data

    server = custom_server(expected_subject, expected_msg, expected_data)
    monkeypatch.setattr("smtplib.SMTP_SSL", server)
    assert instance_fixture.email(expected_subject, expected_msg) == True

def test_email_auth_error(monkeypatch, instance_fixture):
    pass # TODO: have server.sendmail throw this exception

def test_email_general_error(monkeypatch, instance_fixture):
    pass # TODO: have server.sendmail throw this exception
