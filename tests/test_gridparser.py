import pytest

from gridengineapp import GridParser, ArgumentError


def test_grid_parser():
    """Happy path."""
    gp = GridParser()
    gp.add_argument("--hi", action="store_true")
    args = gp.parse_args(["--hi"])
    assert args.hi


def test_grid_parser_exception():
    """A wrong argument raises an exception without exiting."""
    gp = GridParser()
    gp.add_argument("--takes-arg", type=int)
    args = gp.parse_args(["--takes-arg", "37"])
    assert args.takes_arg == 37

    with pytest.raises(ArgumentError, match="expected one argument"):
        gp.parse_args(["--takes-arg"])
