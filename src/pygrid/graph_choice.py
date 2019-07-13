import logging
import networkx as nx

LOGGER = logging.getLogger(__name__)


def jobs_not_done(job_graph, job_done):
    graph = job_graph.copy()  # Copy so we can add "done" attribute.
    check_next = list(nx.topological_sort(graph))
    check_next.reverse()
    remaining_graph = graph.copy()
    while len(remaining_graph) > 0:
        check = check_next.pop()
        if check not in remaining_graph:
            continue
        complete = job_done(check)
        graph.node[check]["done"] = complete
        to_remove = [check]
        if not complete:
            for subsequent in nx.descendants(graph, check):
                graph.node[subsequent]["done"] = False
                to_remove.append(subsequent)
        # If a node is done, an un-done node above it can make
        # it incorrect, so don't mark predecessors as known to be done.
        remaining_graph.remove_nodes_from(to_remove)
    keep = [not_done for not_done in graph
            if not graph.node[not_done]["done"]]
    LOGGER.debug(f"Doing jobs {keep}")
    return nx.subgraph(job_graph, keep)


def job_subset(app, args):
    identifiers = app.job_identifiers(args)
    job_graph = app.job_graph()
    if hasattr(args, "run_dependents") and not args.run_dependents:
        sub_graph = nx.subgraph(job_graph, identifiers)
    else:
        descendants = set(identifiers)
        for identifier in identifiers:
            descend = set(nx.descendants(job_graph, identifier))
            descendants |= descend
        sub_graph = nx.subgraph(job_graph, descendants)
    if hasattr(args, "continue") and getattr(args, "continue"):

        def job_done(job_id):
            return app.job(job_id).done()

        sub_graph = jobs_not_done(sub_graph, job_done)
    return sub_graph


def execution_ordered(graph):
    """
    This iterator orders the nodes
    such that they go depth-first. This is chosen so that the data
    has the most locality during computation. It's not strictly
    depth-first, but depth-first, given that all predecessors must
    be complete before a node executes.
    """
    possible = [n for n in graph if not list(graph.predecessors(n))]
    seen = set()
    while possible:
        node = possible.pop()
        parents_must_complete = set(graph.predecessors(node))
        if node not in seen and not parents_must_complete - seen:
            seen.add(node)
            yield node
            for successor in graph.successors(node):
                possible.append(successor)