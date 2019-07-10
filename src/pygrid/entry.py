from argparse import ArgumentParser


def execution_ordered(graph):
    """
    This orders the nodes
    such that they go depth-first. This is chosen so that the data
    has the most locality during computation. It's not strictly
    depth-first, but depth-first, given that all predecessors must
    be complete before a node executes.
    """
    possible = [n for n in graph if not graph.predecessors(n)]
    seen = set()
    while possible:
        node = possible.pop()
        parents_must_complete = set(graph.predecessors(node))
        if node not in seen and not parents_must_complete - seen:
            seen.add(node)
            yield node
            for successor in graph.successors(node):
                possible.append(successor)


def setup_args_for_job(args, job_id):
    arg_list = list()
    all_args = {under.replace("_", "-"): v for (under, v)
                in args.__dict__.items()}
    all_args.update(job_id.arguments)
    for flag, value in all_args.items():
        if flag in ["grid-engine"]:
            continue
        dash_flag = f"--{flag}"
        if isinstance(value, bool):
            flag_list = [dash_flag]
        elif value is None:
            flag_list = []
        else:
            flag_list = [dash_flag, str(value)]
        arg_list.extend(flag_list)
    arg_list.extend(job_id)
    return arg_list


def qsub_template(resources, holds):
    return resources.update({"h": holds})


def qsub(template, args):
    return "grid_job_id"


def launch_jobs(app, args):
    job_graph = app.job_graph()

    grid_id = dict()
    for job_id in execution_ordered(job_graph):
        job_args = setup_args_for_job(args, job_id)
        holds = [grid_id[jid] for jid in job_graph.predecessors(job_id)]
        template = qsub_template(app.job(job_id).resources, holds)
        grid_job_id = qsub(template, job_args)
        grid_id[job_id] = grid_job_id


def job_subset(app, args):
    job_graph = app.job_graph()
    any_id = job_graph.nodes[0].job_identifier
    

def run_jobs(app, args):
    for job in job_subset(app, args):
        job.run()

def execution_parser():
    parser = ArgumentParser()
    parser.add_argument("--grid-engine", action="store_true")
    return parser


def entry(app, args=None):
    """

    Args:
        app (application.Application): The main application to run.
        args (Namespace|SimpleNamespace): Arguments to the command line.
    """
    parser = execution_parser()
    app.add_arguments(parser)
    args = parser.parse_args(args)
    if args.grid_engine:
        launch_jobs(app, args)
    else:
        run_jobs(app, args)
