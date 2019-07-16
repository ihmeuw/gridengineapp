from pathlib import Path
from time import sleep, time

import pytest

import gridengineapp.submit
from gridengineapp.config import configuration
from gridengineapp.status import check_complete
from gridengineapp.submit import template_to_args, qsub


@pytest.mark.parametrize("template,args", [
    (dict(q="all.q"), ["-q", "all.q"]),
    (dict(v=False), ["-v", "FALSE"]),
    (dict(q="all.q", P="proj"), ["-q", "all.q", "-P", "proj"]),
    (dict(l=dict(a=1, b=2)), ["-l", "a=1,b=2"]),  # noqa: E741
    (dict(l=dict(), P="proj"), ["-P", "proj"]),  # noqa: E741
    (dict(l=dict(archive=True)), ["-l", "archive=TRUE"]),  # noqa: E741
])
def test_template_to_args_happy(template, args):
    assert template_to_args(template) == args


def test_qsub_execute_mock(monkeypatch):
    desired = ["file.sh", "arg1"]

    def whatsit(command, args, **_kwargs):
        if command != "which qsub":
            assert [command] + args == [
                "qsub", "-terse", "-q", "all.q", "file.sh", "arg1"]
            return "mvid"
        else:
            return"qsub"

    monkeypatch.setattr(gridengineapp.submit, "run_check", whatsit)
    template = dict(q="all.q")
    assert qsub(template, desired) == "mvid"


@pytest.fixture
def qsub_template():
    settings = configuration()
    template = dict(
        l=dict(
            h_rt="00:05:00",
            m_mem_free="1G",
            fthread=1,
            archive=True,
        ),
        P=settings["project"],
        q=settings["queues"].split()[0],
    )
    return template


@pytest.mark.parametrize("queue_idx", [0, 1, 2])
def test_live_qsub(
        fair, shared_cluster_tmp, qsub_template, queue_idx
):
    """Test the basic submission.
    This is basically all we will use from qsub.
    Note that it tests the project and queue.
    """
    qsub_template["b"] = "y"
    settings = configuration()
    queues = settings["queues"].split()
    if queue_idx < len(queues):
        qsub_template["q"] = queues[queue_idx]
    else:
        return
    job_name = "echo_test"
    qsub_template["N"] = job_name
    log_path = shared_cluster_tmp / f"live_qsub{queue_idx}.out"
    qsub_template["o"] = log_path
    job_id = qsub(qsub_template, ["/bin/echo", "borlaug"])
    print(f"Using out path {log_path} and job_id {job_id}")

    def this_job(job):
        return job.job_id == job_id

    def check_done():
        return log_path.exists()

    try:
        check_complete(this_job, check_done)
    except TimeoutError as te:
        if te.args[1] == "engine":
            return  # That's OK. It means the queue was slow.
        else:
            assert False, f"timeout for state {te.args[1]}"

    # Lesson learned here: It's better to try to read the file
    # and fail than to ask whether it exists. Apparently the former
    # will succeed sooner on this filesystem.
    start = time()
    slowest_filesystem_metadata_ever = 120
    while time() - start < slowest_filesystem_metadata_ever:
        try:
            dir_list = list(f.name for f in log_path.parent.glob("*"))
            print(f"Looking for {log_path}. Find {dir_list}")
            with log_path.open() as istream:
                contents = istream.read()
            assert "borlaug" in contents
            return
        except FileNotFoundError:
            sleep(2)
    raise AssertionError(f"The file never showed up {log_path}")
