from logging import getLogger
import networkx as nx
from argparse import ArgumentParser
from pygrid import Job, FileEntity, IntegerIdentifier, entry

LOGGER = getLogger(__name__)


class LocationJob(Job):
    def __init__(self, location_id):
        super().__init__()
        self.location_id = location_id
        out_file = f"data/{location_id}.hdf"
        self.outputs.append(FileEntity(out_file))

    @property
    def identifier(self):
        return IntegerIdentifier(self.location_id)

    def run(self):
        self.mock_run()


class Application:
    def __init__(self):
        self._max_level = None

    def add_arguments(self, parser=None):
        if parser is None:
            parser = ArgumentParser()
        parser.add_argument("--max-level", type=int)
        return parser

    def job_graph(self):
        locations = nx.balanced_tree(3, 2, create_using=nx.DiGraph)
        return locations

    def job(self, identifier):
        return LocationJob(identifier)

    def job_identifiers(self, args):
        if hasattr(args, "job_id") and isinstance(args.job_id, int):
            return [IntegerIdentifier(args.job_id)]
        else:
            return self.job_graph().nodes


if __name__ == "__main__":
    app = Application()
    entry(app)
