import io
import pytest
import pandas
from sqlalchemy import create_engine
from src.tables import Service_Periods
from datetime import datetime

@pytest.fixture
def instance_fixture():
    return Service_Periods("sw23", "invalid")

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
    instance = Service_Periods(user, passwd, hostname, db_name)
    assert instance._engine.url == expected.url

def test_constructor_given_engine(dummy_engine):
    engine = dummy_engine[0]
    engine_url = engine.url
    instance = Service_Periods(engine=engine_url)
    assert instance._engine.url == engine.url

def test_index_col(instance_fixture):
    assert instance_fixture._index_col == "service_key"

def test_table_name(instance_fixture):
    assert instance_fixture._table_name == "service_periods"

def test_expected_cols(instance_fixture):
    expected_cols = ["month", "year", "ternary"]
    assert instance_fixture._expected_cols == expected_cols

def test_creation_sql(instance_fixture):
    # This tabbing is not accidental.
    expected = "".join(["""
            CREATE TABLE IF NOT EXISTS """, instance_fixture._schema, ".", instance_fixture._table_name, """
            (
                service_key BIGSERIAL PRIMARY KEY,
                month SMALLINT NOT NULL CHECK ( (month <= 12) AND (month >= 1) ),
                year SMALLINT NOT NULL CHECK (year > 1700),
                ternary SMALLINT NOT NULL CHECK ( (ternary <= 3) AND (ternary >= 1) ),
                UNIQUE (month, year, ternary)
            );"""])
    assert expected == instance_fixture._creation_sql

def test_get_ternary(instance_fixture):
    assert instance_fixture.get_ternary(1) == 1
    assert instance_fixture.get_ternary(4) == 1
    assert instance_fixture.get_ternary(5) == 2
    assert instance_fixture.get_ternary(8) == 2
    assert instance_fixture.get_ternary(9) == 3
    assert instance_fixture.get_ternary(12) == 3

    assert instance_fixture.get_ternary(0) == -1
    assert instance_fixture.get_ternary(-12) == -1
    assert instance_fixture.get_ternary(100) == -1

def test_query_or_insert(monkeypatch, instance_fixture):
    monkeypatch.setattr(instance_fixture, "query_month_year", lambda x, y: 1)
    monkeypatch.setattr(instance_fixture, "insert_one", lambda x, y: 2)
    assert instance_fixture.query_or_insert(1, 1) == 1

    monkeypatch.setattr(instance_fixture, "query_month_year", lambda x, y: None)
    assert instance_fixture.query_or_insert(1, 1) == 2
    

def test_insert_one(instance_fixture):
    class mock_connection():
        def __enter__(self):
            return self
        def __exit__(self, type, value, traceback):
            return
        def execute(self, sql):
            return type('X', (object,), dict(first=lambda: (sql, 0)))
    instance_fixture._engine.connect = lambda: mock_connection()

    expected = "".join(["INSERT INTO ", instance_fixture._schema, ".",
                        instance_fixture._table_name, " (month, year, ternary)"\
                        " VALUES (1, 2020, 1) RETURNING service_key;"])

    assert instance_fixture.insert_one(1, 2020) == expected
