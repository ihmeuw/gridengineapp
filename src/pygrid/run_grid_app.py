import logging
import re

from .argument_handling import setup_args_for_job
from .config import configuration
from .determine_executable import executable_for_job
from .graph_choice import job_subset, execution_ordered
from .qsub_template import QsubTemplate
from .submit import max_run_minutes_on_queue
from .submit import qsub

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


def sanitize_id(job_id_string):
    """Given any job ID, turn it into OK characters for qsub name."""
    recognized = "".join(re.findall(r"[\w_,\- ]", job_id_string))
    return re.sub(r"[ ,\-]+", "_", recognized)


def configure_qsub(name, job_id, resources, holds, args):
    template = QsubTemplate()
    template.N = f"{name}_{sanitize_id(str(job_id))}"
    template.l = dict(
        h_rt=minutes_to_time(resources["run_time_minutes"]),
        fthread=str(resources["threads"]),
        m_mem_free=f"{resources['memory_gigabytes']}G"
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
    return template


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
    for job_id in execution_ordered(job_graph):
        job_args = run_job_under_no_profile(app, arg_list, args_to_remove, job_id)
        holds = list()
        for source, _sink, data in job_graph.in_edges(job_id, data=True):
            if not ("launch" in data and data["launch"]):
                holds.append(grid_id[source])
        template = configure_qsub(
            job_name, job_id, app.job(job_id).resources, holds, args
        )
        grid_job_id = qsub(template, job_args)
        grid_id[job_id] = grid_job_id
