import logging
import re

from .argument_handling import setup_args_for_job
from .config import configuration
from .determine_executable import executable_for_job
from .graph_choice import job_subset, execution_ordered
from .qsub_template import QsubTemplate
from .submit import max_run_minutes_on_queue, qsub

LOGGER = logging.getLogger(__name__)


def run_job_under_no_profile(app, arg_list, args_to_remove, job_id):
    """
    This step takes a script and arguments and
    runs them using a bash command that removes the user's
    profile and bashrc from the environment. We do this because
    it makes the work much more likely to run for another user.
    """
    script = executable_for_job(app)
    job_select = app.job_id_to_arguments(job_id)
    args = setup_args_for_job(args_to_remove, job_select, arg_list)
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
    queues = configuration()["queues"].split()
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


def sanitize_id(job_id_string):
    """Given any job ID, turn it into OK characters for qsub name."""
    recognized = "".join(re.findall(r"[\w_,\- ]", job_id_string))
    return re.sub(r"[ ,\-]+", "_", recognized)


def format_memory(mem_gb):
    if mem_gb < 0.125:
        mem_gb = 0.125
    if abs(mem_gb - round(mem_gb)) > 0.01:
        mem_mb = round(1024 * mem_gb)
        mem_string = f"{mem_mb}M"
    else:
        mem_string = f"{round(mem_gb)}G"
    return mem_string


def configure_qsub(name, job_id, job, holds, args):
    resources = job.resources
    template = QsubTemplate()
    template.N = f"{name}_{sanitize_id(str(job_id))}"
    template.l = dict(  # noqa: E741
        h_rt=minutes_to_time(resources["run_time_minutes"]),
        fthread=str(resources["threads"]),
        m_mem_free=format_memory(resources["memory_gigabytes"])
    )
    if hasattr(args, "rerun_cnt") and args.rerun_cnt:
        template.r = "y"
    if holds:
        template.hold_jid = [str(h) for h in holds]
    if hasattr(args, "project") and args.project is not None:
        template.P = args.project
    else:
        template.P = configuration()["project"]
    template.q = [choose_queue(resources["run_time_minutes"])]
    template.b = "y"
    # Task arrays
    if "task_cnt" in resources and int(resources["task_cnt"]) > 1:
        template.t = f"1-{resources['task_cnt']}"
    return job.configure_qsub(template)


def launch_jobs(app, args, arg_list, args_to_remove):
    """
    Launches grid engine jobs for this app.

    If an edge in a job graph has a "launch" property, set to True,
    then the dependent job will wait until the previous job is
    launched but not wait for it to finish.
    """
    job_graph = job_subset(app, args)
    if hasattr(app, "name"):
        app_name = app.name
    else:
        app_name = app.__class__.__name__
    job_name = app_name + args.run_id

    grid_id = dict()
    for app_job_id in execution_ordered(job_graph):
        job_args = run_job_under_no_profile(
            app, arg_list, args_to_remove, app_job_id)
        holds = list()
        for source, _sink, data in job_graph.in_edges(app_job_id, data=True):
            if not ("launch" in data and data["launch"]):
                # Qsub's grid_engine_id can be 10851099.1-30:1 for tasks.
                grid_job_id = grid_id[source].split(".")[0]
                holds.append(grid_job_id)
        template = configure_qsub(
            job_name, app_job_id, app.job(app_job_id), holds, args
        )
        grid_job_id = qsub(template, job_args)
        grid_id[app_job_id] = grid_job_id
    if len(grid_id) < 20:
        LOGGER.debug(f"Launched {', '.join(grid_id.values())}")
    else:
        LOGGER.debug(f"Launched {len(grid_id)} jobs.")
    return grid_id
