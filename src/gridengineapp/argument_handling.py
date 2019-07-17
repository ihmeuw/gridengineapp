import sys
from argparse import ArgumentParser
from os import environ
from secrets import token_hex
from textwrap import fill


def setup_args_for_job(args_to_remove, job_args, arg_list=None):
    """
    Pass input arguments to the jobs, except for those
    that configure grid engine calls.

    Args:
        args_to_remove (Dict[str,bool]): Map from flag, with
            double-dashes, to whether it has an argument.
        job_args (List[str]): Flags to add to command line to specify
            this particular job.
        arg_list (List[str]): This is sys.argv[1:], but it's
            here only for debugging.

    Returns:
        List[str]: A new set of arguments to pass to child
        processes.
    """
    if arg_list is None:
        arg_list = sys.argv[1:]
    else:
        arg_list = [str(any_arg) for any_arg in arg_list]
    job_flags = [str(job_arg) for job_arg in job_args
                 if str(job_arg).startswith("--")]
    args_to_remove.update({id_flag: True for id_flag in job_flags})
    for dash_flag, has_argument in args_to_remove.items():
        for arg_idx, check_arg in enumerate(arg_list):
            if check_arg.startswith(dash_flag):
                if "=" in check_arg or not has_argument:
                    arg_list = arg_list[:arg_idx] + arg_list[arg_idx + 1:]
                else:
                    arg_list = arg_list[:arg_idx] + arg_list[arg_idx + 2:]
    return arg_list + job_args


def execution_parser():
    parser = ArgumentParser()
    # The keys are flags to remove when calling jobs as processes
    # (outside grid engine), and the values are whether that flag
    # has an argument.
    remove_for_jobs = dict()

    grid = parser.add_argument_group(
        "Grid Engine",
        "Flags that affect running under Grid Engine"
    )
    grid.add_argument("--grid-engine", action="store_true")
    remove_for_jobs["--grid-engine"] = False
    grid.add_argument("--project", type=str, help="project name")
    remove_for_jobs["--project"] = True
    grid.add_argument(
        "--rerun-cnt", type=int,
        help=fill("""
            Turns on rerunning of jobs for this grid engine
            submission and sets the number of times any one job
            is allowed to rerun.
        """),
    )
    grid.add_argument(
        "--run-id", type=str,
        default=token_hex(3),
        help=fill("""
        This is a string identifier that is added to the application
        name in order to make it easier to use qstat, qdel, and such.
        """)
    )
    try:
        # The task id can be the string "undefined"
        task_id = int(environ.get("SGE_TASK_ID", "0"))
    except ValueError:
        task_id = 0
    grid.add_argument(
        "--task-id", type=int,
        default=task_id,
        help=fill("""
        The Grid Engine SGE_TASK_ID value for this task.
        If this isn't a task array, the task_id is 0.
        This is a 1-based value for task arrays.
        """)
    )
    remove_for_jobs["--task-id"] = True

    multiprocess = parser.add_argument_group(
        "Multiprocess",
        "Flags that affect running with multiple processes"
    )
    multiprocess.add_argument(
        "--memory-limit", type=float,
        help=fill("""
        Total gigabytes to use for multiple processes. This tries to
        run the whole job graph on this machine, running within the
        specified memory limit.
        """),
    )
    remove_for_jobs["--memory-limit"] = True

    graph = parser.add_argument_group(
        "Job Graph",
        "Flags that select which jobs should be run."
    )
    graph.add_argument(
        "--continue", action="store_true",
        help=fill("""
            This looks at files on disk or databases, anything
            defined as an Entity in the outputs of jobs, and uses
            that to decide which jobs need to be rerun. If a job
            needs to be rerun, then all jobs that depend on it
            in the graph will be rerun, too.
        """),
    )
    remove_for_jobs["--continue"] = False
    graph.add_argument(
        "--run-dependents", action="store_true",
        help=fill("""
            If one job fails, but other jobs aren't failing, you
            want to restart those jobs that depend on the failed
            job, but you can't use continue because it would
            check for files, and it would rerun all the jobs.
            This option says to run all jobs that depend on
            a particular one.
        """),
    )
    remove_for_jobs["--run-dependents"] = False

    debug = parser.add_argument_group(
        "Debugging and Logging",
        "Flags that affect debugging and logging of jobs."
    )
    debug.add_argument("--verbose-app", action="count", default=0,
                       help="Increase verbosity of logging")
    remove_for_jobs["--verbose-app"] = False
    debug.add_argument("--quiet-app", action="count", default=0,
                       help="Decrease verbosity of logging")
    remove_for_jobs["--quiet-app"] = False
    debug.add_argument(
        "--pdb", action="store_true",
        help="Invoke interactive debugger on error.",
    )
    remove_for_jobs["--pdb"] = False
    debug.add_argument(
        "--mock-job", action="store_true",
        help="Don't run jobs. Ask them to make fake outputs.",

    )
    return parser, remove_for_jobs
