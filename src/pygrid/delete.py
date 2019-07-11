from logging import getLogger
from subprocess import run, PIPE, TimeoutExpired, CalledProcessError

from pygrid.config import configuration

LOGGER = getLogger(__name__)


def qdel(job_list):
    timeout = configuration()["qdel-timeout-seconds"]
    try:
        LOGGER.debug(f"deleting {job_list}")
        qdel_path = run("which qdel", shell=True, stdout=PIPE,
                        universal_newlines=True).stdout.strip()
        run(
            [qdel_path, str(job_list)],
            shell=False, universal_newlines=True, stdout=PIPE, stderr=PIPE,
            timeout=timeout, check=True
        )
    except CalledProcessError as cpe:
        LOGGER.info(f"qdel call {cpe.cmd} failed: {cpe.stderr}")
    except TimeoutExpired:
        LOGGER.info(f"qdel timed out after {timeout}s")
