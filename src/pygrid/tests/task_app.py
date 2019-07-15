"""
Tests don't normally belong here, but we need an installed package
for testing purposes.
"""
from pathlib import Path

import networkx as nx

from pygrid import Job, FileEntity


class SingleJob(Job):
    def __init__(self, base_directory):
        super().__init__()
        out_file = base_directory / f"one.hdf"
        self.outputs["out"] = FileEntity(out_file)

    def run(self):
        self.mock_run()


class Singleton:
    """All this work to run one qsub."""
    def __init__(self):
        self.base_directory = None

    def initialize(self, args):
        self.base_directory = args.base_directory

    @staticmethod
    def add_arguments(parser):
        parser.add_argument(
            "--base-directory", type=Path,
            default=Path(".")
        )
        parser.add_argument(
            "--job-id", type=int
        )
        return parser

    @staticmethod
    def job_id_to_arguments(job_id):
        return [
            "--job-id", job_id
        ]

    def job_identifiers(self, args):
        if hasattr(args, "job_id") and args.job_id is not None:
            return [0]
        else:
            return self.job_graph().nodes

    @staticmethod
    def job_graph():
        """
        Use a tuple as the key in the job graph.
        The tuple is (location_id, sex), where location_id
        is an integer and sex is a string: male, female, or both.
        """
        # This graph, that NetworkX makes, has integer
        # nodes, starting from 0.
        jobs = nx.DiGraph()
        jobs.add_node(0)
        return jobs

    def job(self, _identifier):
        return SingleJob(self.base_directory)


# Here, we intentionally leave off the main guard
# that runs this application, in order to see
# whether the framework can do without it.
