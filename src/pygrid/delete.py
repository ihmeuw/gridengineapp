from logging import getLogger

from .process import run_check

LOGGER = getLogger(__name__)


def qdel(job_list):
    if isinstance(job_list, list):
        job_list = ",".join(str(job_id) for job_id in job_list)
    run_check("qdel", job_list)
