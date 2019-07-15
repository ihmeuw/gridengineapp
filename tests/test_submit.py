from pathlib import Path
from time import sleep, time

import pytest

import pygrid.submit
from pygrid.config import configuration
from pygrid.status import check_complete
from pygrid.submit import template_to_args, qsub


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

    monkeypatch.setattr(pygrid.submit, "run_check", whatsit)
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
        q=settings["queues"][0],
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
    queues = settings["queues"]
    if queue_idx < len(queues):
        qsub_template["q"] = queues[queue_idx]
    else:
        return
    job_name = "echo_test"
    qsub_template["N"] = job_name
    out_path = shared_cluster_tmp / f"live_qsub{queue_idx}.out"
    qsub_template["o"] = out_path
    job_id = qsub(qsub_template, ["/bin/echo", "borlaug"])
    print(f"Using out path {out_path} and job_id {job_id}")

    def this_job(job):
        return job.job_id == job_id

    def check_done():
        return out_path.exists()

    try:
        ran_to_completion = check_complete(this_job, check_done)
    except TimeoutError as te:
        if te.args[1] == "engine":
            return  # That's OK. It means the queue was slow.
        else:
            assert False, f"timeout for state {te.args[1]}"

    if ran_to_completion:
        if not out_path.exists():
            sleep(20)
        with out_path.open() as istream:
            contents = istream.read()
        assert "borlaug" in contents
        out_path.unlink()
