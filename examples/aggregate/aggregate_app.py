from argparse import ArgumentParser
from logging import getLogger
from pathlib import Path
import csv

import networkx as nx

from pygrid import Job, FileEntity

LOGGER = getLogger(__name__)


class PAFJob(Job):
    def __init__(self, cause, base_directory):
        super().__init__()
        self.cause = cause
        self.out_file = base_directory / f"{cause}.csv"
        self.outputs["out"] = FileEntity(self.out_file)

    def run(self):
        with Path(self.out_file).open("w") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([3, 7, 9, str(self.cause)])


class AggregateJob(Job):
    def __init__(self, base_directory):
        super().__init__()
        self.base_directory = base_directory
        self.cause = "aggregate"
        self.out_file = Path(base_directory / f"all.csv")
        self.outputs["out"] = FileEntity(self.out_file)

    def run(self):
        causes = self.base_directory.glob("*.csv")
        with self.out_file.open("w") as csvfile:
            for infile in causes:
                with infile.open("r") as inread:
                    data = inread.read()
                csvfile.write(data)


class PAFApplication:
    def __init__(self):
        self.base_directory = Path(".")
        self.name = self.__class__.__name__
        self.cause_cnt = 3

    def add_arguments(self, parser=None):
        if parser is None:
            parser = ArgumentParser()
        parser.add_argument("--base-directory", type=Path)
        parser.add_argument("--cause-cnt", type=int, default=5)
        parser.add_argument("--job-idx", type=str, help="The job ID")
        return parser

    def initialize(self, args):
        if args.base_directory is not None:
            self.base_directory = args.base_directory
        self.cause_cnt = args.cause_cnt

    def job_graph(self):
        job_graph = nx.DiGraph()
        aggregate = "aggregate"
        job_graph.add_edges_from(
            (f"cause_{chr(97 + i)}", aggregate)
            for i in range(self.cause_cnt)
        )
        return job_graph

    def job(self, identifier):
        if identifier == "aggregate":
            return AggregateJob(self.base_directory)
        else:
            return PAFJob(identifier, self.base_directory)

    def job_identifiers(self, args):
        if hasattr(args, "job_id") and isinstance(args.job_id, str):
            return [args.job_id]
        else:
            return self.job_graph().nodes


# No __main__ for this one. It will be made by the framework.
