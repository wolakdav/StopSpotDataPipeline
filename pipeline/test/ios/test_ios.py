import pytest
import io
from src.ios import IOs

@pytest.fixture
def instance_fixture():
    return IOs()

def test_print_is_wrapper(instance_fixture):
    instance_fixture._print = lambda x, y: "Success!"
    assert instance_fixture.print("") == "Success!"

def test_prompt_is_wrapper(instance_fixture):
    instance_fixture._prompt = lambda x, y: "Success!"
    assert instance_fixture.prompt("") == "Success!"

def test_print_no_obj(capsys, instance_fixture):
    instance_fixture._print("Hello!")
    assert capsys.readouterr().out == "Hello!\n"

def test_print_obj(capsys, instance_fixture):
    obj = ["Pizza", "Pie"]
    instance_fixture._print("Hello!", obj)
    assert capsys.readouterr().out == "Hello!['Pizza', 'Pie']\n"

def test_prompt_unhidden(monkeypatch, instance_fixture):
    expected = "sw23"
    prompt = "> "
    monkeypatch.setattr("sys.stdin", io.StringIO(expected + "\n"))
    result = instance_fixture._prompt(prompt)
    assert result == expected

def test_prompt_hidden(monkeypatch, instance_fixture):
    expected = "fake\n"
    prompt = "> "
    monkeypatch.setattr("getpass.getpass", lambda _: expected)
    result = instance_fixture._prompt(prompt, True)
    assert result == expected
