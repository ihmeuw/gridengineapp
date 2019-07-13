import importlib
from pathlib import Path

import pytest

from pygrid.determine_executable import (
    find_or_create_executable, module_has_main_guard
)


@pytest.fixture
def example_module(examples, monkeypatch):
    """Returns the example module."""

    def pick_module(example, name):
        monkeypatch.syspath_prepend(examples[example])
        return importlib.import_module(name)

    return pick_module


def test_find_or_create_executable_uninstalled_has_init(example_module):
    location_module = example_module("location_hierarchy", "location_app")
    app_class = location_module.Application
    argv0 = find_or_create_executable(app_class)
    assert len(argv0) == 1
    assert Path(argv0[0]).name == "location_app.py"
    assert Path(argv0[0]).exists()


def test_find_or_create_executable_uninstalled_no_init(example_module):
    agg_module = example_module("aggregate", "aggregate_app")
    app_class = agg_module.PAFApplication
    argv0 = find_or_create_executable(app_class)
    assert len(argv0) == 1
    path = Path(argv0[0])
    assert path.name.endswith(".py")
    assert path.exists()
    assert path.name != "aggregate_app.py"


@pytest.mark.parametrize("input,result", [
    ("""if __name__ == "__main__": pass""", True),
    ("3 + 7", False),
    ("if 3 == 7: pass", False),
    ("""if __name__ == "sunshine": pass""", False),
])
def test_module_has_main_guard(input, result):
    assert module_has_main_guard(input) == result
