"""
Tests don't normally belong here, but we need an installed package
for testing purposes.
"""
from pathlib import Path

import networkx as nx

from gridengineapp import Job, FileEntity, entry


class SingleJob(Job):
    def __init__(self, base_directory):
        super().__init__()
        self.base_directory = base_directory

    @property
    def outputs(self):
        out_file = self.base_directory / f"location{self.task_id}.hdf"
        self._outputs["out"] = FileEntity(out_file)
        return self._outputs

    @property
    def resources(self):
        return dict(
            memory_gigabytes=0.2,
            threads=1,
            run_time_minutes=2,
            task_cnt=5,
        )

    def clone_task(self, task_id):
        return super().clone_task(task_id)

    def run(self):
        self.mock_run()


class Countries:
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
        There is only one job, but it's a task array.
        """
        jobs = nx.DiGraph()
        jobs.add_node(0)
        return jobs

    def job(self, _identifier):
        return SingleJob(self.base_directory)


if __name__ == "__main__":
    app = Countries()
    exit(entry(app))
