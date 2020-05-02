import pytest
from sqlalchemy import create_engine
from src.tables import Processed_Days

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

    # TODO: create tests for
    #   insert: valid date, mock connection
    #   insert: bad date
    #   insert: invalid engine
    #   insert: sqlalchemy error
    #
    #   delete: valid date, mock connection
    #   delete: bad date
    #   delete: invalid engine
    #   delete: sqlalchemy error
