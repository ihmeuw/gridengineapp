from functools import lru_cache
from logging import getLogger
from subprocess import run, PIPE, TimeoutExpired, CalledProcessError

LOGGER = getLogger(__name__)
BLOCK_QCALLS = False


@lru_cache(maxsize=16)
def find_full_path(executable):
    """Uses the Bash shell's ``which`` command to find the full path
    to the given command. We could hard-code the command location."""
    return run(
        f"which {executable}", shell=True, stdout=PIPE,
        universal_newlines=True).stdout.strip()


def run_check(executable, arguments, timeout):
    if BLOCK_QCALLS:
        raise RuntimeError(
            f"This unit test needs to be marked to run on cluster")
    try:
        executable_path = find_full_path(executable)
        # Requires the full path, or this call will not work.
        process_out = run(
            [str(arg) for arg in [executable_path] + arguments],
            shell=False, universal_newlines=True, stdout=PIPE, stderr=PIPE,
            timeout=timeout, check=True
        )
    except CalledProcessError as cpe:
        LOGGER.info(f"qsub call {cpe.cmd} failed: {cpe.stderr}")
        return None
    except TimeoutExpired:
        LOGGER.info(f"qsub timed out after {timeout}s")
        return None
    return process_out.stdout.strip()
