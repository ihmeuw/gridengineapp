from pygrid.main import setup_args_for_job
from pygrid.identifier import IntegerIdentifier

import pytest


@pytest.mark.parametrize("to_remove,arglist,expected", [
    (dict(), [], ["--job-id", "7"]),
    (dict(), ["--job-id", "9"], ["--job-id", "7"]),
    (dict(), ["--howdy"], ["--howdy", "--job-id", "7"]),
    (dict(), ["--howdy", "4"], ["--howdy", "4", "--job-id", "7"]),
    (dict(), ["--job-id", "9", "--howdy"], ["--howdy", "--job-id", "7"]),
    ({"--grid-engine": False}, ["--grid-engine"], ["--job-id", "7"]),
    ({"--queue": True}, ["--queue", "all.q"], ["--job-id", "7"]),
    ({"--queue": True}, [], ["--job-id", "7"]),
    ({"--queue": True}, ["-v"], ["-v", "--job-id", "7"]),
])
def test_args_for_int_job(to_remove, arglist, expected):
    job_id = IntegerIdentifier(7)
    result = setup_args_for_job(to_remove, job_id, arglist)
    assert result == expected
