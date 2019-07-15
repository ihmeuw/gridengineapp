from argparse import ArgumentParser

import networkx as nx

from .job import Job


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
            return [args.job_id]
        else:
            return self.job_graph().nodes


def check_application(app):
    parser = ArgumentParser()
    args = app.add_arguments(parser).parse_args([])
    app.initialize(args)
    graph = app.job_graph()
    assert isinstance(graph, nx.DiGraph)
    identifiers = app.job_identifiers(args)
    assert len(identifiers) == len(graph.nodes)
