"""
Tests don't belong in the main repository, but there
have to be tests of applications that are installed
into packages, so this is the only way I can think of to test
that.
"""
from pathlib import Path

import networkx as nx

from pygrid import Job, FileEntity, entry


class LocationSexJob(Job):
    def __init__(self, location, sex, base_directory):
        super().__init__()
        self.location_id = location
        self.sex = sex
        out_file = base_directory / f"{location}_{sex}.hdf"
        self.outputs["out"] = FileEntity(out_file)

    def run(self):
        self.mock_run()


class AggregateJob(Job):
    def __init__(self, base_directory):
        super().__init__()
        out_file = base_directory / "all.hdf"
        self.outputs["out"] = FileEntity(out_file)

    def run(self):
        self.mock_run()


class CascadeIsh:
    def __init__(self):
        self.base_directory = None

    def initialize(self, args):
        self.base_directory = args.base_directory

    def add_arguments(self, parser):
        parser.add_argument(
            "--base-directory", type=Path,
            default=Path(".")
        )
        parser.add_argument(
            "--location-id", type=int
        )
        parser.add_arugment(
            "--sex", type=str
        )
        return parser

    def job_id_to_arguments(self, job_id):
        return [
            "--location-id", str(job_id[0]),
            "--sex", job_id[1]
        ]

    def job_identifiers(self, args):
        has_loc = args.location_id is not None
        has_sex = args.sex is not None
        if has_loc and has_sex:
            return [(args.location_id, args.sex)]
        else:
            return self.job_graph().nodes

    def job_graph(self):
        locations = nx.balanced_tree(3, 2, create_using=nx.DiGraph)
        jobs = nx.DiGraph()
        globe = (1, "both")
        jobs.add_node(globe)
        for zero_begin, zero_end in locations.edges():
            loc_begin, loc_end = (1 + zero_begin, 1 + zero_end)
            for sex in ["male", "female"]:
                if loc_begin == 1:
                    jobs.add_edge(globe, (loc_end, sex))
                else:
                    jobs.add_edge((loc_begin, sex), (loc_end, sex))
        aggregate = (1, "aggregate")
        most_detailed = [
            last for last in jobs
            if not list(jobs.successors(last))
        ]
        for bottom in most_detailed:
            jobs.add_edge(bottom, aggregate)
        return jobs

    def job(self, identifier):
        location_id, sex = identifier
        if sex == "aggregate":
            return AggregateJob(self.base_directory)
        else:
            return LocationSexJob(location_id, sex, self.base_directory)


if __name__ == "__main__":
    exit(entry(CascadeIsh()))
