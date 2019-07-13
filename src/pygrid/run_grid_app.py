import logging
import re
import sys
from getpass import getuser
from hashlib import sha224
from importlib import import_module
from os import linesep
from pathlib import Path

from pygrid import qsub
from pygrid.argument_handling import setup_args_for_job
from pygrid.config import configuration
from pygrid.graph_choice import job_subset, execution_ordered
from pygrid.qsub_template import QsubTemplate
from pygrid.submit import max_run_minutes_on_queue

LOGGER = logging.getLogger(__name__)


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


def run_job_under_no_profile(arg_list, args_to_remove, job_id):
    """
    This step takes a script and arguments and
    runs them using a bash command that removes the user's
    profile and bashrc from the environment. We do this because
    it makes the work much more likely to run for another user.
    """
    script = executable_for_job()
    args = setup_args_for_job(args_to_remove, job_id, arg_list)
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
    """
    job_graph = job_subset(app, args)

    grid_id = dict()
    for job_id in execution_ordered(job_graph):
        job_args = run_job_under_no_profile(arg_list, args_to_remove, job_id)
        holds = [grid_id[jid] for jid in job_graph.predecessors(job_id)]
        template = configure_qsub(
            app.name, job_id, app.job(job_id).resources, holds, args
        )
        grid_job_id = qsub(template, job_args)
        grid_id[job_id] = grid_job_id
