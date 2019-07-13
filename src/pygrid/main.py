import faulthandler
import logging
from bdb import BdbQuit
from enum import Enum
from types import SimpleNamespace

import networkx as nx

from pygrid.argument_handling import (
    setup_args_for_job, execution_parser
)
from pygrid.determine_executable import subprocess_executable
from pygrid.graph_choice import job_subset, execution_ordered
from pygrid.run_grid_app import launch_jobs
from .exceptions import NodeMisconfigurationError
from .multiprocess import graph_do
from .restart import restart_count

LOGGER = logging.getLogger(__name__)


def run_jobs(app, args):
    faulthandler.enable()
    try:
        job_graph = job_subset(app, args)
        for identifier in execution_ordered(job_graph):
            if not args.mock_job:
                app.job(identifier).run()
            else:
                app.job(identifier).mock_run()

    except BdbQuit:
        pass
    except Exception:  # Too broad be we re-raise.
        if args.pdb:
            # invokes debugger when an exception happens.
            import pdb
            import traceback

            traceback.print_exc()
            pdb.post_mortem()
        else:
            raise


def multiprocess_jobs(app, args, arg_list, args_to_remove):
    job_graph = job_subset(app, args)

    def run_next(completed_jobs):
        keep = [job for job in job_graph.nodes
                if job not in completed_jobs]
        remaining = nx.subgraph(job_graph, keep)
        runnable = [rem for rem in execution_ordered(remaining)
                    if not list(job_graph.predecessors(rem))]
        job_descriptions = dict()
        for job_id in runnable:
            environment_base, main_path = subprocess_executable()
            args = setup_args_for_job(args_to_remove, job_id, arg_list)
            job = app.job(job_id)
            job_descriptions[job_id] = SimpleNamespace(
                memory=job.resources["memory"],
                args=[environment_base, main_path] + args,
            )
        return job_descriptions

    graph_do(run_next, args.memory_limit)


class GridEngineReturnCodes(Enum):
    """
    These are return codes that Grid Engine recognizes.
    Any other return codes are treated as OK. If you don't
    return 100, then it will try to run the next job that's holding
    for this job.
    """
    OK = 0
    RequestRestart = 99
    FailAndDeleteHoldingJobs = 100


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
    """
    parser, args_to_remove = execution_parser()
    app.add_arguments(parser)
    args = parser.parse_args(arg_list)
    logging.basicConfig(level=logging.INFO + 10 * (args.quiet - args.verbose))
    restart_cnt = restart_count()
    try:
        app.initialize(args)
        if args.grid_engine:
            launch_jobs(app, args, arg_list, args_to_remove)
        elif args.memory_limit:
            multiprocess_jobs(app, args, arg_list, args_to_remove)
        else:
            run_jobs(app, args)
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
