from argparse import ArgumentParser

import networkx as nx

from .job import Job


class IntegerIdentifier:
    def __init__(self, id):
        self._id = id

    @property
    def arguments(self):
        return ["--job-id", str(self._id)]

    def __eq__(self, other):
        if not isinstance(other, IntegerIdentifier):
            return False
        return other._id == self._id

    def __hash__(self):
        return self._id

    def __repr__(self):
        return f"JobIdentifier({self._id})"


class Application:
    def __init__(self):
        pass

    def add_arguments(self, parser=None):
        if parser is None:
            parser = ArgumentParser()
        return parser

    def job_graph(self):
        return nx.DiGraph()

    def job(self, identifier):
        return Job(identifier)

    def job_identifiers(self, args):
        if hasattr(args, "job_id") and isinstance(args.job_id, int):
            return [IntegerIdentifier(args.job_id)]
        else:
            return self.job_graph().nodes
