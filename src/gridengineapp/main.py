import faulthandler
import logging
import sys
from bdb import BdbQuit
from enum import Enum
from inspect import getmembers, ismethod
from types import SimpleNamespace

import networkx as nx

from .argument_handling import (
    setup_args_for_job, execution_parser
)
from .config import configuration
from .determine_executable import subprocess_executable
from .graph_choice import job_subset, execution_ordered
from .run_grid_app import launch_jobs
from .exceptions import NodeMisconfigurationError
from .multiprocess import graph_do
from .restart import restart_count

LOGGER = logging.getLogger(__name__)


def iterate_tasks(job, command_line_task_id):
    """
    Walk through tasks to run from a job. If the task_id is nonzero,
    then limit it to that task_id.

    Args:
        job (Job): The job object.
        command_line_task_id (int): A Task ID chosen on the command
            line. This is how a job learns it should do a particular
            task. This value is set by ``SGE_TASK_ID`` environment
            variable, if that's set.

    Returns:
        A job instance.
    """
    if "task_cnt" in job.resources and job.resources["task_cnt"] > 0:
        if command_line_task_id is not None and command_line_task_id > 0:
            yield job.clone_task(command_line_task_id)
        else:
            for task_id in range(1, 1 + job.resources["task_cnt"]):
                yield job.clone_task(task_id)
    else:
        yield job


def run_jobs(app, args):
    faulthandler.enable()
    try:
        job_graph = job_subset(app, args)
        for identifier in execution_ordered(job_graph):
            for task in iterate_tasks(app.job(identifier), args.task_id):
                if not args.mock_job:
                    task.run()
                else:
                    task.mock_run()

    except BdbQuit:
        pass
    except Exception:  # Too broad be we re-raise.
        if args.pdb:
            # invokes debugger when an exception happens.
            if sys.stdout.fileno() != 1:
                LOGGER.info(f"Not invoking pdb because stdout is captured")
                raise
            import pdb
            import traceback

            traceback.print_exc()
            pdb.post_mortem()
        else:
            raise


def job_task_ids(job):
    """Yields task IDs. If this isn't an array job, the only ID is 0."""
    if "task_cnt" in job.resources and int(job.resources["task_cnt"]) > 1:
        yield from range(1, 1 + int(job.resources["task_cnt"]))
    else:
        yield from [0]


def expand_task_arrays(job_graph, app):
    """Take a job graph and expand the jobs into tasks.
    Every job has at least one task. Jobs that are task
    arrays can have more tasks. If the node type for
    a job graph is Type, then the node type for a
    task graph is the tuple (Type, task_id)."""
    # Pull out the task counts.
    task_graph = nx.DiGraph()
    for job_id in nx.topological_sort(job_graph):
        job = app.job(job_id)
        task_predecessors = list()
        for job_pred in job_graph.predecessors(job_id):
            for pred_idx in job_task_ids(app.job(job_pred)):
                task_predecessors.append((job_pred, pred_idx))
        # Add nodes before edges in case there are no edges.
        task_graph.add_nodes_from(
            (job_id, task_job) for task_job in job_task_ids(job)
        )
        task_graph.add_edges_from(
            (task_pred, (job_id, task_job))
            for task_pred in task_predecessors
            for task_job in job_task_ids(job)
        )
    return task_graph


def find_runnable(remaining):
    runnable = list()
    for remain_job in execution_ordered(remaining):
        has_dependencies = False
        for _u, _v, data in remaining.in_edges(remain_job, data=True):
            # Don't count this particular edge as a dependency.
            if not ("launch" in data and data["launch"]):
                has_dependencies = True
        if not has_dependencies:
            runnable.append(remain_job)
    return runnable


class RunNext:
    def __init__(self, app, task_graph, arg_list, args_to_remove):
        self.app = app
        self.task_graph = task_graph
        self.arg_list = arg_list
        self.args_to_remove = args_to_remove

    def __call__(self, completed_jobs):
        """This is a functor, not a class."""
        keep = [job for job in self.task_graph.nodes
                if job not in completed_jobs]
        remaining = nx.subgraph(self.task_graph, keep)
        runnable = find_runnable(remaining)
        return self.construct_descriptions(runnable)

    def construct_descriptions(self, runnable):
        job_descriptions = dict()
        for job_id, task_id in runnable:
            python_executable, argv0 = subprocess_executable(self.app)
            job_select = self.app.job_id_to_arguments(job_id)
            args = setup_args_for_job(
                self.args_to_remove, job_select, self.arg_list)
            if task_id > 0:
                args.extend(["--task-id", str(task_id)])
            job = self.app.job(job_id)
            job_descriptions[(job_id, task_id)] = SimpleNamespace(
                memory=job.resources["memory_gigabytes"],
                args=[str(python_executable)] + argv0 + args,
            )
        return job_descriptions


def multiprocess_jobs(app, command_args, arg_list, args_to_remove):
    job_graph = job_subset(app, command_args)
    task_graph = expand_task_arrays(job_graph, app)
    LOGGER.debug(f"{len(task_graph)} tasks to run")
    run_next = RunNext(app, task_graph, arg_list, args_to_remove)
    graph_do(run_next, command_args.memory_limit)


class GridEngineReturnCodes(Enum):
    """
    These are return codes that Grid Engine recognizes.
    Any other return codes are treated as OK. If you don't
    return 100, then it will try to run the next job that's holding
    for this job. "man sge_diagnostics" to see more.
    """
    OK = 0
    RequestRestart = 99
    FailAndDeleteHoldingJobs = 100


def configure_from_application(app):
    """If the application has a configuration method,
    then call it. That method should return a ConfigParser instance
    that has a section for this package."""
    app_methods = {name: func for (name, func) in getmembers(app, ismethod)}
    if "configuration" in app_methods:
        configuration(app.configuration())


def grid_child_guard(work, args):
    """Runs Python so that its return codes match those described
    in sge_diagnostics, to demand failure or restart."""
    restart_cnt = restart_count()
    try:
        work()
    except NodeMisconfigurationError as nme:
        LOGGER.exception(nme)
        if (
                hasattr(args, "rerun_cnt") and
                args.rerun_cnt and
                restart_cnt < args.rerun_cnt
        ):
            return GridEngineReturnCodes.RequestRestart.value
        else:
            return GridEngineReturnCodes.FailAndDeleteHoldingJobs.value
    except Exception as exc:
        LOGGER.exception(exc)
        return GridEngineReturnCodes.FailAndDeleteHoldingJobs.value
    return GridEngineReturnCodes.OK.value


def entry(app, arg_list=None):
    """
    This starts the application. Use it with::

        if __name__ == "__main__":
            application = MyApplication()
            entry(application)

    Args:
        app (application.Application): The main application to run.
        arg_list (Namespace|SimpleNamespace): Arguments to the command line.
            This is usually None and is used for testing.
            Pass this around instead of using sys.argv because
            pytest makes it hard to set sys.argv.
    """
    configure_from_application(app)
    parser, args_to_remove = execution_parser()
    app.add_arguments(parser)
    args = parser.parse_args(arg_list)
    offset = 10 * (args.quiet_app - args.verbose_app)
    logging.basicConfig(level=logging.INFO + offset)

    def work():
        app.initialize(args)
        if args.grid_engine:
            launch_jobs(app, args, arg_list, args_to_remove)
        elif args.memory_limit:
            multiprocess_jobs(app, args, arg_list, args_to_remove)
        else:
            run_jobs(app, args)

    grid_child_guard(work, app)
