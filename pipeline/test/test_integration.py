import os
import sys
from datetime import datetime

import pytest
import sqlalchemy

from src.client import _Client
from src.ios import ios


# Fixtures
@pytest.fixture(autouse=True)
def setup_and_clean_db(monkeypatch):
    # Setup env...
    monkeypatch.setenv("PIPELINE_ENV_DATA", "true")
    monkeypatch.setenv("PORTAL_USER", "DanD")
    monkeypatch.setenv("PORTAL_PASSWD", "DanD")
    monkeypatch.setenv("PORTAL_HOSTNAME", "westbot.westus.cloudapp.azure.com")
    monkeypatch.setenv("PORTAL_DB_NAME", "DanD_db")
    monkeypatch.setenv("PORTAL_SCHEMA", "aperture")
    monkeypatch.setenv("PIPELINE_USER", "DanD")
    monkeypatch.setenv("PIPELINE_PASSWD", "DanD")
    monkeypatch.setenv("PIPELINE_HOSTNAME", "westbot.westus.cloudapp.azure.com")
    monkeypatch.setenv("PIPELINE_DB_NAME", "DanD_db")
    monkeypatch.setenv("PIPELINE_SCHEMA", "hive")

    assert os.environ["PIPELINE_ENV_DATA"]

    # Setup table..
    ios.start("./test/.it_test_log.txt")
    client = _Client(read_env_data=True)
    assert isinstance(client.ctran._engine, sqlalchemy.engine.Connectable)
    res = client.ctran.create_table(ctran_sample_path="test/assets/integration/")
    assert res is True

    ds = datetime.strptime('2019-03-01', "%Y-%m-%d")
    de = datetime.strptime('2019-03-07', "%Y-%m-%d")

    df = client.ctran.query_date_range(ds, de)
    assert len(df.index) == 21

    yield

    # Cleanup table...
    ios.stop()
    assert isinstance(client.ctran._engine, sqlalchemy.engine.Connectable)
    res = client.ctran.delete_table()
    assert res is True

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


# @pytest.fixture
# def client():
#     return _Client(read_env_data=True)
#
#
# @pytest.fixture
# def ctran(client):
#     return client.ctran
#
#
# @pytest.fixture
# def flagged(client):
#     return client.flagged


@pytest.fixture
def set_sys_argv_range_query_1():
    sys.argv = [sys.argv[0], '--date-start=2019-03-01', '--date-end=2019-03-01']


@pytest.fixture
def set_sys_argv_range_query_2():
    sys.argv = [sys.argv[0], '--date-start=2019-03-05', '--date-end=2019-03-05']


# Helper Functions
def find_error(lf="./test/.it_test_log.txt", search_for="ERROR"):
    try:
        with open(lf) as f:
            if search_for in f.read():
                return True
    except FileNotFoundError as e:
        print(e)
    return False


# Tests
def test_query_date_range_with_bad_env_vars_fails(monkeypatch, set_sys_argv_range_query_1):
    monkeypatch.setenv("PORTAL_USER", "foo")
    client = _Client()
    df = client.ctran._query_table("SELECT COUNT(*) FROM " + client.ctran._schema + "." + client.ctran._table_name)
    assert find_error(search_for="role \"foo\" does not exist")
    assert df is None
    assert find_error() is True
    with pytest.raises(SystemExit) as sys_ext:
        client.main()  # Passes
        assert sys_ext.value.code == 2


def test_query_date_range_with_good_credentials_passes(monkeypatch, set_sys_argv_range_query_1):
    client = _Client()
    df = client.ctran._query_table("SELECT COUNT(*) FROM " + client.ctran._schema + "." + client.ctran._table_name)
    assert df is not None
    assert isinstance(client.ctran._engine, sqlalchemy.engine.Connectable)
    assert find_error() is False
    client.main()


def test_query_date_range_returns_expected(set_sys_argv_range_query_1):
    client = _Client()
    assert isinstance(client.ctran._engine, sqlalchemy.engine.Connectable)
    client.main()
    assert find_error() is False


