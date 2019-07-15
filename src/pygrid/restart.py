from getpass import getuser
from os import environ
from pathlib import Path

from .config import configuration


def restart_count():
    """
    How many times has this job restarted?
    Writes to a file in the logging directory in order to record
    the number of restarts. Grid Engine will tell a task that it
    has restarted but not how many times. This makes a file
    with Job ID and Task Id and the ending ``.restart``, with
    one character in it per restart.

    Returns:
        int: The number of restarts.
    """
    clipped_restart_cnt = environ.get("RESTARTED", 0)
    if clipped_restart_cnt == 0:
        restart_cnt = 0
    else:
        template = configuration()["restart-file-location"]
        temporary_path = Path(template.format(user=getuser()))
        temporary_path.mkdir(parents=True, exist_ok=True)
        job_id = environ.get("JOB_ID", "unknown-job")
        task_id = environ.get("SGE_TASK_ID", "unknown-task")
        marker_path = temporary_path / f"{job_id}.{task_id}.restart"
        if marker_path.exists():
            with marker_path.open("r") as check:
                restart_cnt = len(check.read()) + 1
        else:
            restart_cnt = 1
        with marker_path.open("a") as mark:
            mark.write(".")

    return restart_cnt
