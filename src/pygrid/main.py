import logging
import sys
from argparse import ArgumentParser
from importlib import import_module
from pathlib import Path
from tempfile import gettempdir
from uuid import uuid4

import networkx as nx

from .config import configuration
from .qsub_template import QsubTemplate
from .submit import qsub

LOGGER = logging.getLogger(__name__)


def execution_ordered(graph):
    """
    This orders the nodes
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


def setup_args_for_job(args, job_id):
    """
    Pass input arguments to the jobs, except for those
    that configure grid engine calls.
    """
    arg_list = [str(executable_for_job())]
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
    return arg_list


def executable_for_job():
    main_module = import_module("__main__")
    if hasattr(main_module, "__file__"):
        main_path = Path(main_module.__file__).resolve()
    else:
        raise RuntimeError(f"Cannot find the main")
    environment_base = Path(sys.exec_prefix)
    activate = environment_base / "bin" / "activate"
    if activate.exists():
        enter_environment = f"source {activate}"
    else:
        enter_environment = f"conda activate {environment_base}"
    run_program = f"python {main_path} $*"
    script = configuration()["shell-file"]
    replacements = dict(
        enter_environment=enter_environment,
        run_program=run_program,
    )
    raw_script = script.format(**replacements)
    # gettempdir gets the Grid Engine temp within /tmp.
    tmp = Path(gettempdir()) / (str(uuid4()) + ".sh")
    with tmp.open("w") as script_out:
        script_out.write(raw_script)
    return tmp


def minutes_to_time(duration_minutes):
    hours = duration_minutes // 60
    minutes = duration_minutes - hours * 60
    return f"{hours:02}:{minutes:02}:00"


def configure_qsub(name, job_id, resources, holds, args):
    template = QsubTemplate()
    template.N = f"{name}_{job_id}"
    template.l = dict(
        h_rt=minutes_to_time(resources["run_time_minutes"]),
        fthread=str(resources["threads"]),
        m_mem_free=f"{resources['memory_gigabytes']}G"
    )
    if holds:
        template.hold_jid = [str(h) for h in holds]
    if hasattr(args, "P") and args.P is not None:
        template.P = args.P
    template.q = ["all.q"]
    return template


def launch_jobs(app, args):
    job_graph = app.job_graph()

    grid_id = dict()
    for job_id in execution_ordered(job_graph):
        job_args = setup_args_for_job(args, job_id)
        holds = [grid_id[jid] for jid in job_graph.predecessors(job_id)]
        template = configure_qsub(
            app.name, job_id, app.job(job_id).resources, holds, args
        )
        grid_job_id = qsub(template, job_args)
        grid_id[job_id] = grid_job_id


def job_subset(app, args):
    identifiers = app.job_identifiers(args)
    job_graph = app.job_graph()
    sub_graph = nx.subgraph(job_graph, identifiers)
    return (
        app.job(identifier) for identifier in execution_ordered(sub_graph)
    )


def run_jobs(app, args):
    for job in job_subset(app, args):
        job.run()


def execution_parser():
    parser = ArgumentParser()
    parser.add_argument("--grid-engine", action="store_true")
    parser.add_argument("-v", "--verbose", action="count", default=0,
                        help="Increase verbosity of logging")
    parser.add_argument("-q", "--quiet", action="count", default=0,
                        help="Decrease verbosity of logging")
    parser.add_argument("-P", type=str, help="project name")
    return parser


def entry(app, args=None):
    """
    This starts the application. Use it with::

        if __name__ == "__main__":
            application = MyApplication()
            entry(application)

    Args:
        app (application.Application): The main application to run.
        args (Namespace|SimpleNamespace): Arguments to the command line.
            This is usually None and is used for testing.
    """
    parser = execution_parser()
    app.add_arguments(parser)
    args = parser.parse_args(args)
    logging.basicConfig(level=logging.INFO + 10 * (args.quiet - args.verbose))
    if args.grid_engine:
        launch_jobs(app, args)
    else:
        run_jobs(app, args)
