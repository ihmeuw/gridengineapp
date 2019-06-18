import pytest

import pygrid


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
            pytest.skip(f"specify --fair to run tests requiring fair cluster")

        pygrid.process.BLOCK_QCALLS = False
