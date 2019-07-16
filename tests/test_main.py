from argparse import ArgumentParser
from logging import getLogger
from pathlib import Path
from secrets import token_hex
from time import sleep
from types import SimpleNamespace

import networkx as nx
import pytest

from gridengineapp import (
    Job, FileEntity, IntegerIdentifier, entry, check_complete,
)
from gridengineapp.argument_handling import setup_args_for_job
from gridengineapp.graph_choice import jobs_not_done
from gridengineapp.main import job_task_cnt

LOGGER = getLogger(__name__)


@pytest.mark.parametrize("to_remove,arglist,expected", [
    (dict(), [], ["--job-id", "7"]),
    (dict(), ["--job-id", "9"], ["--job-id", "7"]),
    (dict(), ["--howdy"], ["--howdy", "--job-id", "7"]),
    (dict(), ["--howdy", "4"], ["--howdy", "4", "--job-id", "7"]),
    (dict(), ["--job-id", "9", "--howdy"], ["--howdy", "--job-id", "7"]),
    ({"--grid-engine": False}, ["--grid-engine"], ["--job-id", "7"]),
    ({"--queue": True}, ["--queue", "all.q"], ["--job-id", "7"]),
    ({"--queue": True}, [], ["--job-id", "7"]),
    ({"--queue": True}, ["-v"], ["-v", "--job-id", "7"]),
])
def test_args_for_int_job(to_remove, arglist, expected):
    """For jobs within a qsub, arguments are stripped."""
    result = setup_args_for_job(to_remove, ["--job-id", "7"], arglist)
    assert result == expected


@pytest.mark.parametrize("edge_list,not_done,expected", [
    ([(0, 1)], [0, 1], [0, 1]),
    ([(0, 1)], [0], [0, 1]),
    ([(0, 1)], [1], [1]),
    ([(0, 1), (0, 2)], [1], [1]),
    ([(0, 1), (0, 2)], [0], [0, 1, 2]),
    ([(0, 1), (0, 2), (1, 3), (2, 3)], [1], [1, 3]),
    ([(0, 1), (0, 2), (1, 3), (2, 3)], [0], [0, 1, 2, 3]),
    ([(0, 1), (0, 2), (1, 3), (2, 3)], [3], [3]),
])
def test_jobs_not_done(edge_list, not_done, expected):
    """A job that isn't done means descendants aren't done."""
    graph = nx.DiGraph()
    graph.add_edges_from(edge_list)

    def job_done(job_id):
        return job_id not in not_done

    result = jobs_not_done(graph, job_done)
    assert set(result) == set(expected)
    assert isinstance(result, nx.DiGraph)


class LocationJob(Job):
    def __init__(self, location_id, base_directory):
        super().__init__()
        self.location_id = location_id
        out_file = base_directory / f"data/{location_id}.hdf"
        self.outputs["out"] = FileEntity(out_file)

    @property
    def identifier(self):
        return IntegerIdentifier(self.location_id)

    def run(self):
        LOGGER.info(f"Running job {self.location_id}")
        self.mock_run()


class Application:
    def __init__(self):
        self._max_level = None
        self.name = "testapp37"
        self.base_directory = Path(".")

    def add_arguments(self, parser=None):
        if parser is None:
            parser = ArgumentParser()
        parser.add_argument("--max-level", type=int)
        parser.add_argument("--base-directory", type=Path)
        IntegerIdentifier.add_arguments(parser)
        return parser

    def initialize(self, args):
        if args.base_directory is not None:
            self.base_directory = args.base_directory

    @staticmethod
    def job_id_to_arguments(job_id):
        return ["--job-id", str(job_id)]

    def job_graph(self):
        locations = nx.balanced_tree(3, 2, create_using=nx.DiGraph)
        job_graph = nx.DiGraph()
        job_graph.add_edges_from(
            (IntegerIdentifier(u), IntegerIdentifier(v))
            for (u, v) in locations.edges
        )
        return job_graph

    def job(self, identifier):
        return LocationJob(int(identifier), self.base_directory)

    def job_identifiers(self, args):
        if hasattr(args, "job_id") and isinstance(args.job_id, int):
            return [IntegerIdentifier(args.job_id)]
        else:
            return self.job_graph().nodes


def test_local_single_job(tmp_path):
    args = ["--job-id", "7", "--base-directory", str(tmp_path)]
    app = Application()
    entry(app, args)
    file_seven = tmp_path / "data" / "7.hdf"
    assert file_seven.exists()
    assert len(list(file_seven.parent.glob("*.hdf"))) == 1


def test_local_all_jobs(tmp_path):
    args = ["--base-directory", str(tmp_path)]
    app = Application()
    entry(app, args)
    data_dir = tmp_path / "data"
    assert len(list(data_dir.glob("*.hdf"))) == 13


def test_local_continue_jobs(tmp_path):
    args = ["--job-id", "0", "--base-directory", str(tmp_path)]
    app = Application()
    entry(app, args)
    data = tmp_path / "data"
    data0 = data / "0.hdf"
    assert data0.exists()
    mtime = data0.stat().st_mtime
    sleep(1)

    args = ["--continue", "--verbose-app", "--base-directory", str(tmp_path)]
    app = Application()
    entry(app, args)

    # This says we didn't modify the file that was already there.
    assert data0.stat().st_mtime == mtime
    assert len(list(data.glob("*.hdf"))) == 13


def test_remote_continue_jobs(fair, shared_cluster_tmp):
    """
    Given one job that's done, show this does the rest of the jobs.
    """
    base = shared_cluster_tmp

    # Start by making a single one of 13 files.
    data = base / "data"
    args = [
        "--job-id", "0", "--base-directory", str(base)
    ]
    app = Application()
    entry(app, args)
    data0 = data / "0.hdf"
    assert data0.exists()
    mtime = data0.stat().st_mtime
    sleep(1)

    # Then ask the framework to continue.
    unique = token_hex(4)
    app_full_name = app.name + unique
    args = [
        "--grid-engine", "--run-id", unique,
        "--continue", "--verbose-app", "--base-directory", str(base)
    ]
    entry(app, args)

    def identify_job(j):
        return j.name.startswith(app_full_name)

    def check_done():
        return len(list(data.glob("*.hdf"))) == 13

    timeout_seconds = 3 * 60
    try:
        check_complete(identify_job, check_done, timeout_seconds)
    except TimeoutError as te:
        if te.args[1] == "engine":
            return  # This means the queue was slow.
        else:
            raise

    # This says we didn't modify the file that was already there.
    assert data0.stat().st_mtime == mtime
    # But all of the jobs are done.
    assert len(list(data.glob("*.hdf"))) == 13


def test_job_task_cnt_none():
    job = Job()
    assert job_task_cnt(job) == 1


def test_job_task_cnt_with_tasks():
    job = SimpleNamespace(resources=dict(task_cnt=12))
    assert job_task_cnt(job) == 12


def test_expand_task_arrays_happy():
    graph