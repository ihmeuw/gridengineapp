from argparse import ArgumentParser
from logging import getLogger
from pathlib import Path

import networkx as nx

from pygrid import Job, FileEntity, entry

LOGGER = getLogger(__name__)


class LocationJob(Job):
    def __init__(self, location_id, base_directory, please_fail=False):
        super().__init__()
        self.location_id = location_id
        out_file = base_directory / f"data/{location_id}.hdf"
        self.outputs["out"] = FileEntity(out_file)
        self.please_fail = please_fail

    def run(self):
        LOGGER.info(f"Running job {self.location_id}")
        assert not self.please_fail
        self.mock_run()


class LocationApp:
    def __init__(self):
        self._max_level = None
        self.base_directory = Path(".")
        self.fail_for = None

    def initialize(self, args):
        if args.base_directory is not None:
            self.base_directory = args.base_directory
        self.fail_for = args.fail_for

    @staticmethod
    def add_arguments(parser=None):
        if parser is None:
            parser = ArgumentParser()
        parser.add_argument("--max-level", type=int)
        parser.add_argument("--base-directory", type=Path)
        parser.add_argument(
            "--fail-for", type=int,
            help="""
                Run this command with the arguments::
                
                    python location_app.py --job-id 7 --fail-for 7 --pdb
                    
                and it will drop into the debugger.
            """,
        )
        parser.add_argument("--job-id", type=int, help="The job ID")
        return parser

    @staticmethod
    def job_id_to_arguments(job_id):
        return ["--job-id", str(job_id)]

    def job_identifiers(self, args):
        if hasattr(args, "job_id") and isinstance(args.job_id, int):
            return [args.job_id]
        else:
            return self.job_graph().nodes

    def job_graph(self):
        locations = nx.balanced_tree(3, 2, create_using=nx.DiGraph)
        return locations

    def job(self, identifier):
        please_fail = identifier == self.fail_for
        return LocationJob(identifier, self.base_directory, please_fail)


if __name__ == "__main__":
    app = LocationApp()
    exit(entry(app))
