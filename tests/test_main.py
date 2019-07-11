from pygrid.main import setup_args_for_job, jobs_not_done
from pygrid.identifier import IntegerIdentifier
import networkx as nx
import pytest


from argparse import ArgumentParser
from logging import getLogger
from pathlib import Path

import networkx as nx

from pygrid import Job, FileEntity, IntegerIdentifier, entry

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
    job_id = IntegerIdentifier(7)
    result = setup_args_for_job(to_remove, job_id, arglist)
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
        self.outputs.append(FileEntity(out_file))

    @property
    def identifier(self):
        return IntegerIdentifier(self.location_id)

    def run(self):
        LOGGER.info(f"Running job {self.location_id}")
        self.mock_run()


class Application:
    def __init__(self):
        self._max_level = None
        self.base_directory = Path(".")

    @property
    def name(self):
        return "location_app"

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

    args = ["--continue", "-v", "--base-directory", str(tmp_path)]
    app = Application()
    entry(app, args)

    # This says we didn't modify the file that was already there.
    assert data0.stat().st_mtime == mtime
    assert len(list(data.glob("*.hdf"))) == 13
