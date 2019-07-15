from argparse import ArgumentParser

import networkx as nx


def check_application(app):
    parser = ArgumentParser()
    args = app.add_arguments(parser).parse_args([])
    app.initialize(args)
    graph = app.job_graph()
    assert isinstance(graph, nx.DiGraph)
    identifiers = app.job_identifiers(args)
    assert len(identifiers) == len(graph.nodes)
