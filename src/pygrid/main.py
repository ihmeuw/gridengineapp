import logging
import re
import sys
from argparse import ArgumentParser
from getpass import getuser
from hashlib import sha224
from importlib import import_module
from os import linesep
from pathlib import Path

import networkx as nx

from .config import configuration
from .qsub_template import QsubTemplate
from .submit import qsub, max_run_minutes_on_queue

LOGGER = logging.getLogger(__name__)


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


def setup_args_for_job(args_to_remove, job_id, arg_list=None):
    """
    Pass input arguments to the jobs, except for those
    that configure grid engine calls.

    Args:
        args_to_remove (Dict[str,bool]): Map from flag, with
            double-dashes, to whether it has an argument.
        job_id: An identifier.
        arg_list (List[str]): This is sys.argv[1:], but it's
            here only for debugging.

    Returns:
        List[str]: A new set of arguments to pass to child
        processes.
    """
    if arg_list is None:
        arg_list = sys.argv[1:]
    job_args = job_id.arguments
    job_flags = [job_arg for job_arg in job_args
                 if job_arg.startswith("--")]
    args_to_remove.update({id_flag: True for id_flag in job_flags})
    for dash_flag, has_argument in args_to_remove.items():
        for arg_idx, check_arg in enumerate(arg_list):
            if check_arg.startswith(dash_flag):
                if "=" in check_arg or not has_argument:
                    arg_list = arg_list[:arg_idx] + arg_list[arg_idx + 1:]
                else:
                    arg_list = arg_list[:arg_idx] + arg_list[arg_idx + 2:]
    return arg_list + job_args


def executable_for_job():
    main_module = import_module("__main__")
    if hasattr(main_module, "__file__"):
        main_path = Path(main_module.__file__).resolve()
    else:
        raise RuntimeError(f"Cannot find the main")
    environment_base = Path(sys.exec_prefix)
    activate = environment_base / "bin" / "activate"
    commands = ["#!/bin/bash"]
    if activate.exists():
        commands.append(f"source {activate}")
    else:
        conda_sh = environment_base / "etc" / "profile.d" / "conda.sh"
        if conda_sh.exists():
            commands.append(f". {conda_sh}")
        commands.append(f"conda activate {environment_base}")
    commands.append(f"python {main_path} $*")
    commands.append("")
    command_lines = linesep.join(commands)

    shell_dir = Path(configuration()["qsub-shell-file-directory"].format(
        user=getuser()
    ))
    shell_dir.mkdir(parents=True, exist_ok=True)
    hash = sha224()
    hash.update(command_lines.encode())
    filename = f"{hash.hexdigest()}.sh"
    tmp = shell_dir / filename
    if not tmp.exists():
        LOGGER.debug(f"Writing {tmp} shell file.")
        with tmp.open("w") as script_out:
            script_out.write(command_lines)
    else:
        LOGGER.debug(f"Using existing shell file {tmp}.")
    return tmp


def run_job_under_no_profile(args_to_remove, job_id):
    """
    This step takes a script and arguments and
    runs them using a bash command that removes the user's
    profile and bashrc from the environment. We do this because
    it makes the work much more likely to run for another user.
    """
    script = executable_for_job()
    args = setup_args_for_job(args_to_remove, job_id)
    return ["/bin/bash", "--noprofile", "--norc", script] + args


def minutes_to_time(duration_minutes):
    hours = duration_minutes // 60  # Not limited to 24 hours.
    minutes = duration_minutes - hours * 60
    return f"{hours:02}:{minutes:02}:00"


def choose_queue(run_time_minutes):
    """
    Pick the queue that has the fewest total minutes
    that are longer than those requested.

    Args:
        run_time_minutes (int): minutes required after which
            the job is killed.

    Returns:
        str: The name of the queue to use.
    """
    queues = configuration()["queues"]
    acceptable = list()
    for queue in queues:
        queue_minutes = max_run_minutes_on_queue(queue)
        if queue_minutes > run_time_minutes:
            acceptable.append((queue_minutes, queue))
    acceptable.sort()
    if len(acceptable) > 0:
        return acceptable[0][1]
    else:
        raise RuntimeError(
            f"No queue long enough for {run_time_minutes} "
            f"among the queues {queues}."
        )


def configure_qsub(name, job_id, resources, holds, args):
    template = QsubTemplate()
    underscore = re.sub(r"[ ,\-]+", "_", str(job_id))
    sanitized = "".join(re.findall(r"[\w_]", underscore))
    template.N = f"{name}_{sanitized}"
    template.l = dict(
        h_rt=minutes_to_time(resources["run_time_minutes"]),
        fthread=str(resources["threads"]),
        m_mem_free=f"{resources['memory_gigabytes']}G"
    )
    if holds:
        template.hold_jid = [str(h) for h in holds]
    if hasattr(args, "project") and args.project is not None:
        template.P = args.project
    else:
        template.P = configuration()["project"]
    template.q = [choose_queue(resources["run_time_minutes"])]
    template.b = "y"
    return template


def launch_jobs(app, args, args_to_remove):
    """
    Launches grid engine jobs for this app.
    """
    job_graph = job_subset(app, args)

    grid_id = dict()
    for job_id in execution_ordered(job_graph):
        job_args = run_job_under_no_profile(args_to_remove, job_id)
        holds = [grid_id[jid] for jid in job_graph.predecessors(job_id)]
        template = configure_qsub(
            app.name, job_id, app.job(job_id).resources, holds, args
        )
        grid_job_id = qsub(template, job_args)
        grid_id[job_id] = grid_job_id


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
    sub_graph = nx.subgraph(job_graph, identifiers)
    if getattr(args, "continue"):

        def job_done(job_id):
            return app.job(job_id).done()

        sub_graph = jobs_not_done(sub_graph, job_done)
    return sub_graph


def run_jobs(app, args):
    job_graph = job_subset(app, args)
    for identifier in execution_ordered(job_graph):
        app.job(identifier).run()


def execution_parser():
    parser = ArgumentParser()
    # The keys are flags to remove when calling jobs as processes
    # (outside grid engine), and the values are whether that flag
    # has an argument.
    remove_for_jobs = dict()
    parser.add_argument("--grid-engine", action="store_true")
    remove_for_jobs["--grid-engine"] = False
    parser.add_argument("-v", "--verbose", action="count", default=0,
                        help="Increase verbosity of logging")
    parser.add_argument("-q", "--quiet", action="count", default=0,
                        help="Decrease verbosity of logging")
    parser.add_argument("--project", type=str, help="project name")
    remove_for_jobs["--project"] =True
    parser.add_argument("--continue", action="store_true")
    remove_for_jobs["--continue"] = False
    return parser, remove_for_jobs


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
    parser, args_to_remove = execution_parser()
    app.add_arguments(parser)
    args = parser.parse_args(args)
    logging.basicConfig(level=logging.INFO + 10 * (args.quiet - args.verbose))
    app.initialize(args)
    if args.grid_engine:
        launch_jobs(app, args, args_to_remove)
    else:
        run_jobs(app, args)
