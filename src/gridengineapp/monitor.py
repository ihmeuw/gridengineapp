import logging
from time import time, sleep

from gridengineapp import qstat_short

LOGGER = logging.getLogger(__name__)
STATECHART = dict(
    initial=dict(timeout=60),
    engine=dict(timeout=600),
    done=dict(timeout=0),
)
"""
Only care about three states, the initial submission,
whether qstat has said it sees the file,
and done, whether that's out of qstat or that the
file exists.
"""


def check_complete(identify_job, check_done, timeout=60 * 60):
    """
    Submit a job and check that it ran.
    If the job never shows up in the queue, and
    it didn't run, that's a failure. If it shows up in
    the queue and goes over the timeout, we abandon it,
    because these are tests.

    Args:
        identify_job (function): True if it's this job.
        check_done (function): True if job is done.
        timeout (float): How many seconds to wait until
            calling the job lost.

    Returns:
        None
    """
    state = "initial"
    last = time()
    dead_to_me = {"deleted", "suspended"}
    state_chart = STATECHART.copy()
    state_chart["engine"]["timeout"] = timeout
    while state != "done" and not check_done():
        my_jobs = qstat_short()
        this_job = [j for j in my_jobs if identify_job(j)]
        if len(this_job) > 0:
            LOGGER.debug(f"Found jobs {[j.name for j in this_job]}")
            if state == "initial":
                last = time()
                state = "engine"
            for check_job in this_job:
                assert not (check_job.status & dead_to_me)
        elif len(this_job) == 0 and state == "engine":
            LOGGER.debug(f"The job isn't in qstat.")
            return
        else:
            LOGGER.debug(f"No jobs showed up after {time() - last}s")
        state_timeout = state_chart[state]["timeout"]
        if time() - last > state_timeout:
            raise TimeoutError(f"Job exceded {state_timeout}.", state)
        sleep(15)
