import importlib
from secrets import token_hex

import pytest

from pygrid import entry, check_complete


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


def test_location_app_scenario_processes_grid(
        example_module, fair, shared_cluster_tmp
):
    location_module = example_module("location_hierarchy", "location_app")
    app = location_module.Application()
    unique = token_hex(3)
    args = ["--base-directory", str(shared_cluster_tmp),
            "--grid-engine", "--run-id", unique]
    entry(app, args)

    def identify_job(j):
        return unique in j.name

    def check_done():
        return (shared_cluster_tmp / "data" / "12.hdf").exists()

    check_complete(identify_job, check_done)

    assert len(list((shared_cluster_tmp / "data").glob("*.hdf"))) == 13
