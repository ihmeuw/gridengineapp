import importlib
import logging
import sys
from secrets import token_hex
from time import sleep, time

import pytest

from pygrid import entry, check_complete
from pygrid.application import check_application
from pygrid.tests.cascade_app import CascadeIsh
from pygrid.tests.task_app import Singleton


@pytest.fixture
def example_module(examples, monkeypatch):
    """Returns the example module. The examples
    fixture gives the path to the examples directory."""

    def pick_module(example, name):
        monkeypatch.syspath_prepend(examples[example])
        return importlib.import_module(name)

    return pick_module


def file_metadata_is_slow(check_done):
    start = time()
    it_couldnt_take_longer_than_this_could_it = 120
    while time() - start < it_couldnt_take_longer_than_this_could_it:
        if check_done():
            return
        sleep(2)
    check_done()


def test_location_app_functions(example_module, tmp_path):
    location_module = example_module("location_hierarchy", "location_app")
    app = location_module.LocationApp()
    args = ["--base-directory", str(tmp_path)]
    entry(app, args)
    assert len(list((tmp_path / "data").glob("*.hdf"))) == 13


def test_location_app_processes_parallel(example_module, tmp_path):
    location_module = example_module("location_hierarchy", "location_app")
    app = location_module.LocationApp()
    args = ["--base-directory", str(tmp_path), "--memory-limit", "2"]
    entry(app, args)
    assert len(list((tmp_path / "data").glob("*.hdf"))) == 13


def test_location_app_processes_grid(
        example_module, fair, shared_cluster_tmp
):
    location_module = example_module("location_hierarchy", "location_app")
    app = location_module.LocationApp()
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


def test_drop_into_pdb(example_module, tmp_path, caplog):
    """Tests that we reach the correct code path for pdb."""
    caplog.set_level(logging.INFO)
    location_module = example_module("location_hierarchy", "location_app")
    app = location_module.LocationApp()
    args = ["--base-directory", str(tmp_path),
            "--job-id", "7", "--fail-for", "7", "--pdb"]
    if sys.stdout.fileno() != 1:
        entry(app, args)
        assert "Not invoking pdb" in caplog.text
    # else you don't want to interactively debug this way.


def test_aggregate_app_functions(example_module, tmp_path):
    location_module = example_module("aggregate", "aggregate_app")
    app = location_module.PAFApplication()
    cause_cnt = 3
    args = ["--base-directory", str(tmp_path), "--cause-cnt", str(cause_cnt)]
    entry(app, args)
    assert len(list(tmp_path.glob("*.csv"))) == cause_cnt + 1


def test_aggregate_app_parallel(example_module, tmp_path):
    location_module = example_module("aggregate", "aggregate_app")
    app = location_module.PAFApplication()
    cause_cnt = 3
    args = ["--base-directory", str(tmp_path), "--cause-cnt", str(cause_cnt),
            "--memory-limit", "2"]
    entry(app, args)
    assert len(list(tmp_path.glob("*.csv"))) == cause_cnt + 1


def test_aggregate_app_grid(example_module, fair, shared_cluster_tmp):
    location_module = example_module("aggregate", "aggregate_app")
    app = location_module.PAFApplication()
    unique = token_hex(3)
    cause_cnt = 3
    tmp_path = shared_cluster_tmp / "agg_app_grid"
    args = ["--base-directory", str(tmp_path), "--cause-cnt", str(cause_cnt),
            "--grid-engine", "--run-id", unique]
    entry(app, args)

    def identify_job(j):
        return unique in j.name

    def check_done():
        return (tmp_path / "d.csv").exists()

    check_complete(identify_job, check_done)

    assert len(list(tmp_path.glob("*.csv"))) == cause_cnt + 1


def test_task_app_create():
    app = Singleton()
    check_application(app)


def test_single_functions(tmp_path):
    app = Singleton()
    args = ["--base-directory", str(tmp_path)]
    entry(app, args)
    assert (tmp_path / "one.hdf").exists()


def test_single_parallel(tmp_path):
    app = Singleton()
    args = ["--base-directory", str(tmp_path),
            "--memory-limit", "2"]
    entry(app, args)
    assert (tmp_path / "one.hdf").exists()


def test_single_grid(fair, shared_cluster_tmp):
    app = Singleton()
    base = shared_cluster_tmp / "test_single_grid"
    unique = token_hex(3)
    args = ["--base-directory", str(base),
            "--grid-engine", "--run-id", unique]
    entry(app, args)

    def identify_job(j):
        return unique in j.name

    def check_done():
        return (base / "one.hdf").exists()

    check_complete(identify_job, check_done)
    file_metadata_is_slow(check_done)


def test_cascade_app_create():
    app = CascadeIsh()
    check_application(app)


def test_cascade_function(tmp_path):
    app = CascadeIsh()
    args = ["--base-directory", str(tmp_path)]
    entry(app, args)
    assert (tmp_path / "all.hdf").exists()


def test_cascade_parallel(tmp_path):
    app = CascadeIsh()
    args = ["--base-directory", str(tmp_path),
            "--memory-limit", "2"]
    entry(app, args)
    assert (tmp_path / "all.hdf").exists()


def test_cascade_grid(fair, shared_cluster_tmp):
    tmp_path = shared_cluster_tmp / "test_cascade_grid"
    app = CascadeIsh()
    unique = token_hex(3)
    args = ["--base-directory", str(tmp_path),
            "--grid-engine", "--run-id", unique]
    entry(app, args)

    def identify_job(j):
        return unique in j.name

    def check_done():
        return (tmp_path / "all.hdf").exists()

    check_complete(identify_job, check_done)
    file_metadata_is_slow(check_done)
