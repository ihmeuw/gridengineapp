from argparse import ArgumentParser
from logging import getLogger
from pathlib import Path

import networkx as nx

from pygrid import Job, FileEntity, IntegerIdentifier, entry

LOGGER = getLogger(__name__)


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

    def done(self):
        errors = [output.validate() for output in self.outputs]
        return not errors


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


if __name__ == "__main__":
    app = Application()
    exit(entry(app))
