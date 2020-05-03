import pytest
import datetime
from sqlalchemy import create_engine
from src.tables import Processed_Days

g_is_valid = None
g_expected = None

@pytest.fixture
def instance_fixture():
    return Processed_Days("sw23", "invalid")

@pytest.fixture
def dummy_engine():
    user = "sw23"
    passwd = "invalid"
    hostname = "localhost"
    db_name = "idk_something"
    engine_info = "".join(["postgresql://", user, ":", passwd, "@", hostname, "/", db_name])
    return create_engine(engine_info), user, passwd, hostname, db_name

# This fixture uses g_is_valid and g_expected. It will not reset those values
# before or after execution.
@pytest.fixture
def custom_connect():
    class custom_connect():
        def execute(self, sql):
            global g_is_valid
            global g_expected

            if sql != g_expected:
                g_is_valid = False
            else:
                g_is_valid = True

    return custom_connect

def test_constructor_build_engine(dummy_engine):
    expected, user, passwd, hostname, db_name = dummy_engine
    instance = Processed_Days(user, passwd, hostname, db_name)
    assert instance._engine.url == expected.url

def test_constructor_given_engine(dummy_engine):
    engine = dummy_engine[0]
    engine_url = engine.url
    instance = Processed_Days(engine=engine_url)
    assert instance._engine.url == engine.url

def test_index_col(instance_fixture):
    assert instance_fixture._index_col == "day"

def test_table_name(instance_fixture):
    assert instance_fixture._table_name == "processed_days"

def test_expected_cols(instance_fixture):
    expected_cols = []
    assert instance_fixture._expected_cols == expected_cols

def test_creation_sql(instance_fixture):
    # This tabbing is not accidental.
    expected = "".join(["""
            CREATE TABLE IF NOT EXISTS """, instance_fixture._schema, ".", instance_fixture._table_name, """
            (
                day DATE PRIMARY KEY
            );"""])
    assert expected == instance_fixture._creation_sql

def test_insert_happy(custom_connect, instance_fixture):
    global g_is_valid
    global g_expected
    day = "2020-02-02"
    date = datetime.datetime.strptime(day, "%Y-%m-%d")
    g_expected = "".join(["INSERT INTO ", instance_fixture._schema, ".", instance_fixture._table_name,
                    " (", instance_fixture._index_col, ") VALUES ('",
                    str(date.year), "/", str(date.month), "/", str(date.day),
                    "') ON CONFLICT DO NOTHING;"])
    instance_fixture._engine.connect = custom_connect
    assert instance_fixture.insert(day) == True
    assert g_is_valid == True

def test_insert_bad_day(instance_fixture):
    assert instance_fixture.insert("20234234") == False

def test_insert_invalid_engine(instance_fixture):
    instance_fixture._engine = None
    assert instance_fixture.insert("2020-02-02") == False

def test_insert_sqlalchemy_error(instance_fixture):
    # Since this table is fake, SQLalchemy will not be able to find it, which
    # will cause this to fail.
    assert instance_fixture.insert("2020-02-02") == False

def test_delete_happy(custom_connect, instance_fixture):
    global g_is_valid
    global g_expected
    day = "2020-02-02"
    date = datetime.datetime.strptime(day, "%Y-%m-%d")
    g_expected = "".join(["DELETE FROM ", instance_fixture._schema, ".", instance_fixture._table_name,
                       " WHERE ", instance_fixture._index_col, " IN ('", str(date.year), "/", str(date.month), "/", str(date.day), "');"])
    instance_fixture._engine.connect = custom_connect
    assert instance_fixture.delete(day) == True
    assert g_is_valid == True

def test_delete_bad_day(instance_fixture):
    assert instance_fixture.delete("20234234") == False

def test_delete_invalid_engine(instance_fixture):
    instance_fixture._engine = None
    assert instance_fixture.delete("2020-02-02") == False

def test_delete_sqlalchemy_error(instance_fixture):
    # Since this table is fake, SQLalchemy will not be able to find it, which
    # will cause this to fail.
    assert instance_fixture.delete("2020-02-02") == False
