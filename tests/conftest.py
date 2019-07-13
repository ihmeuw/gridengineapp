from getpass import getuser
from pathlib import Path

import pytest

import pygrid.process
from pygrid.config import configuration

pygrid.process.BLOCK_QCALLS = True


def pytest_addoption(parser):
    group = parser.getgroup("pygrid")
    group.addoption("--fair", action="store_true",
                    help="run functions requiring access to fair cluster")


@pytest.fixture
def fair(request):
    return FairDbFuncArg(request)


class FairDbFuncArg:
    """
    Uses a pattern from https://pytest.readthedocs.io/en/2.0.3/example/attic.html
    """
    def __init__(self, request):
        if not request.config.getoption("fair"):
            pytest.skip(
                f"specify --fair to run tests requiring fair cluster")

        pygrid.process.BLOCK_QCALLS = False


@pytest.fixture(scope="session")
def shared_cluster_tmp(tmp_path_factory):
    cluster_tmp = configuration()["cluster-tmp"]
    tmp_path = Path(cluster_tmp.format(user=getuser())) / "tmp"
    if Path(*tmp_path.parts[:2]).exists():
        # the fixture still gets made, even if fair isn't chosen.
        tmp_path.mkdir(parents=True, exist_ok=True)
        tmp_path_factory._basetemp = tmp_path
        return tmp_path_factory.mktemp("run")
    else:
        return None


@pytest.fixture(scope="session")
def examples():
    """
    Returns rooted paths to examples in the examples directory.

    Returns:
        Dict[str,str]: Name of example to absolute path of example.
    """
    test_dir = Path(__file__).resolve().parent
    subdirs = (test_dir.parent / "examples").glob("*")
    dirs = [path for path in subdirs if path.is_dir()]
    fixtures = {example.name: example for example in dirs}
    return fixtures
