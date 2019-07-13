import importlib

import pytest

from pygrid import entry


@pytest.fixture
def example_module(examples, monkeypatch):
    """Returns the example module."""

    def pick_module(example, name):
        monkeypatch.syspath_prepend(examples[example])
        return importlib.import_module(name)

    return pick_module


def test_location_app_scenario_functions(example_module, tmp_path):
    location_module = example_module("location_hierarchy", "location_app")
    app = location_module.Application()
    args = ["--base-directory", str(tmp_path)]
    entry(app, args)
    assert len(list((tmp_path / "data").glob("*.hdf"))) == 13


def test_location_app_scenario_processes(example_module, tmp_path):
    location_module = example_module("location_hierarchy", "location_app")
    app = location_module.Application()
    args = ["--base-directory", str(tmp_path), "--memory-limit", "2"]
    entry(app, args)
    assert len(list((tmp_path / "data").glob("*.hdf"))) == 13



def test_tmp_path(fair, shared_cluster_tmp):
    assert shared_cluster_tmp.exists()
