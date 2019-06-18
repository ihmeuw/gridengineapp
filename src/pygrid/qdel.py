from subprocess import run, PIPE, CalledProcessError, TimeoutExpired

from pygrid.qstat import LOGGER, QSTAT_TIMEOUT


def qdel(job_list):
    try:
        LOGGER.debug(f"deleting {job_list}")
        qdel_path = run("which qdel", shell=True, stdout=PIPE,
                         universal_newlines=True).stdout.strip()
        run(
            [qdel_path, str(job_list)],
            shell=False, universal_newlines=True, stdout=PIPE, stderr=PIPE,
            timeout=QSTAT_TIMEOUT, check=True
        )
    except CalledProcessError as cpe:
        LOGGER.info(f"qdel call {cpe.cmd} failed: {cpe.stderr}")
    except TimeoutExpired:
        LOGGER.info(f"qdel timed out after {QSTAT_TIMEOUT}s")