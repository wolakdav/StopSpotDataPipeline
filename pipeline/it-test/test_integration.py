import os
import sys
from datetime import datetime

import pytest
import sqlalchemy
from _pytest.monkeypatch import MonkeyPatch

from src.client import _Client
from src.config import config
from src.ios import ios


# CONSTANTS
FAKE_CONFIG = "./it-test/assets/integration/fake_config.json"
EMPTY_CONFIG = "./it-test/assets/integration/empty_config.json"


CONFIG_LOAD = config.load
IOS_PROMPT = ios.prompt


DATE_START = "Please enter the start date (YYYY/MM/DD): "
DATE_END = "Please enter the end   date (YYYY/MM/DD): "
USERNAME = "Enter username: "
PASSWORD = "Enter password: "
HOSTNAME = "Enter hostname: "
DATABASE = "Enter the database's name: "
SCHEMA = "Enter the table's schema: "


# CLASSES
class FakeInput:
    def __init__(self, replace=None, replace_with=None):
        self.replaced = replace
        self.inputs = dict()
        self.inputs[DATE_START] = "2019/03/01"
        self.inputs[DATE_END] = "2019/03/01"
        self.inputs[USERNAME] = ""
        self.inputs[PASSWORD] = ""
        self.inputs[HOSTNAME] = ""
        self.inputs[DATABASE] = ""
        self.inputs[SCHEMA] = ""

        if replace is not None and replace_with is not None:
            self.inputs[replace] = replace_with


# FIXTURES
@pytest.fixture
def setup_and_clean_env(monkeypatch):
    setup_env(monkeypatch)

    assert os.environ["PIPELINE_ENV_DATA"]

    yield

    teardown_env(monkeypatch)


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    mkp = MonkeyPatch()
    setup_env(mkp)

    # Setup table..
    replace_config(FAKE_CONFIG)
    client = _Client(read_env_data=True)
    assert isinstance(client.ctran._engine, sqlalchemy.engine.Connectable)
    res = client.ctran.create_table(ctran_sample_path="./it-test/assets/integration/")
    assert res is True

    ds = datetime.strptime('2019-03-01', "%Y-%m-%d")
    de = datetime.strptime('2019-03-07', "%Y-%m-%d")

    df = client.ctran.query_date_range(ds, de)
    assert len(df.index) == 21


@pytest.fixture(scope="session", autouse=True)
def teardown_db():
    mkp = MonkeyPatch()

    yield mkp

    # Cleanup table...
    replace_config(FAKE_CONFIG)
    client = _Client(read_env_data=True)
    assert isinstance(client.ctran._engine, sqlalchemy.engine.Connectable)
    res = client.ctran.delete_table()
    assert res is True
    teardown_env(mkp)
    config.load = CONFIG_LOAD
    ios.prompt = IOS_PROMPT


@pytest.fixture
def set_sys_argv_range_query_1():
    sys.argv = [sys.argv[0], '--date-start=2019-03-01', '--date-end=2019-03-01']


@pytest.fixture
def set_sys_argv_range_query_2():
    sys.argv = [sys.argv[0], '--date-start=2019-03-05', '--date-end=2019-03-05']


@pytest.fixture
def mock_it_config():
    replace_config(FAKE_CONFIG)


@pytest.fixture
def mock_empty_config():
    replace_config(EMPTY_CONFIG)


# HELPER FUNCTIONS
def replace_config(fn):
    CONFIG_LOAD(filename=fn, read_env_data=True, debug=False)
    config.load = lambda filename=FAKE_CONFIG, read_env_data=False, debug=False: True


@pytest.fixture
def inputs(request):
    def get_response(prompt="", hide_input=False):
        assert prompt in request.param.inputs
        print(prompt + request.param.inputs.get(prompt))
        return request.param.inputs.get(prompt)

    ios.prompt = get_response

    yield request.param

    ios.prompt = IOS_PROMPT


def setup_env(monkeypatch):
    # Setup env...
    monkeypatch.setenv("PIPELINE_ENV_DATA", "true")
    monkeypatch.setenv("PORTAL_USER", "")
    monkeypatch.setenv("PORTAL_PASSWD", "")
    monkeypatch.setenv("PORTAL_HOSTNAME", "")
    monkeypatch.setenv("PORTAL_DB_NAME", "")
    monkeypatch.setenv("PORTAL_SCHEMA", "")
    monkeypatch.setenv("PIPELINE_USER", "")
    monkeypatch.setenv("PIPELINE_PASSWD", "")
    monkeypatch.setenv("PIPELINE_HOSTNAME", "")
    monkeypatch.setenv("PIPELINE_DB_NAME", "")
    monkeypatch.setenv("PIPELINE_SCHEMA", "")


def teardown_env(monkeypatch):
    # Setup env...
    monkeypatch.delenv("PIPELINE_ENV_DATA")
    monkeypatch.delenv("PORTAL_USER")
    monkeypatch.delenv("PORTAL_PASSWD")
    monkeypatch.delenv("PORTAL_HOSTNAME")
    monkeypatch.delenv("PORTAL_DB_NAME")
    monkeypatch.delenv("PORTAL_SCHEMA")
    monkeypatch.delenv("PIPELINE_USER")
    monkeypatch.delenv("PIPELINE_PASSWD")
    monkeypatch.delenv("PIPELINE_HOSTNAME")
    monkeypatch.delenv("PIPELINE_DB_NAME")
    monkeypatch.delenv("PIPELINE_SCHEMA")


def find_print(cap, search_for="ERROR"):
    out, err = cap.readouterr()
    sys.stdout.write(out)
    sys.stderr.write(err)
    return search_for in out or search_for in err


def run():
    client = _Client()
    client._get_menu_option = lambda min_value, max_value, cli_symbol="> ": 0
    client.main()


# TESTS

# Test of interactive prompt for user credentials for Portal
# Includes:
#   - Test of perfect user input
#   - Test of bad username
#   - Test of bad database name
# @pytest.mark.parametrize(
#     'inputs',
#     (FakeInput(),
#      FakeInput(USERNAME, "foo"),
#      FakeInput(DATABASE, "foo")),
#     indirect=True
# )
# def test_capture_input(inputs, mock_empty_config, capsys, set_sys_argv_range_query_1):
#     # Force the system to read user input
#     config._data.pop("portal_user", None)
#     assert "portal_user" not in config._data
#
#     # Run main
#     run()
#
#     assert find_print(capsys, "Please enter credentials for Portals database with the C-Tran table.")
#
#     # Check which input was replaced with bad data, if any
#     # Look for the appropriate error message
#     bad_input = inputs.replaced
#
#     if bad_input is None:
#         assert not find_print(capsys)
#     elif bad_input == USERNAME:
#         assert find_print(capsys, "role \"foo\" does not exist")
#     elif bad_input == DATABASE:
#         assert find_print(capsys, "database \"foo\" does not exist")
#
#
# def test_query_date_range_with_bad_portal_env_user_vars_fails(monkeypatch, mock_it_config, setup_and_clean_env, capsys, set_sys_argv_range_query_1):
#     monkeypatch.setenv("PORTAL_USER", "foo")
#     run()
#     assert find_print(capsys, "role \"foo\" does not exist")
#
#
# def test_query_date_range_with_bad_portal_env_db_name_vars_fails(monkeypatch, mock_it_config, setup_and_clean_env, capsys, set_sys_argv_range_query_1):
#     monkeypatch.setenv("PORTAL_DB_NAME", "foo")
#     run()
#     assert find_print(capsys, "database \"foo\" does not exist")
#
#
# def test_query_date_range_with_bad_portal_env_schema_vars_fails(monkeypatch, mock_it_config, setup_and_clean_env, capsys, set_sys_argv_range_query_1):
#     monkeypatch.setenv("PORTAL_SCHEMA", "foo")
#     run()
#     assert find_print(capsys, "relation \"foo.ctran_data\" does not exist")
#
#
# def test_query_date_range_with_bad_pipeline_env_user_vars_fails(monkeypatch, mock_it_config, setup_and_clean_env, capsys, set_sys_argv_range_query_1):
#     monkeypatch.setenv("PIPELINE_USER", "foo")
#     run()
#     assert find_print(capsys, "role \"foo\" does not exist")
#
#
# def test_query_date_range_with_bad_pipeline_env_db_name_vars_fails(monkeypatch, mock_it_config, setup_and_clean_env, capsys, set_sys_argv_range_query_1):
#     monkeypatch.setenv("PIPELINE_DB_NAME", "foo")
#     run()
#     assert find_print(capsys, "database \"foo\" does not exist")
#
#
# def test_query_date_range_with_bad_pipeline_env_schema_vars_fails(monkeypatch, mock_it_config, setup_and_clean_env, capsys, set_sys_argv_range_query_1):
#     monkeypatch.setenv("PIPELINE_SCHEMA", "foo")
#     run()
#     assert find_print(capsys, "relation \"foo.service_periods\" does not exist")
