import networkx as nx
import pytest

from gridengineapp.run_grid_app import sanitize_id


@pytest.mark.parametrize("input,output", [
    ("myname", "myname"),
    ("sal62", "sal62"),
    ("blah,foo", "blah_foo"),
    ("blah, foo", "blah_foo"),
    ("blah, fo+o", "blah_foo"),
    ("b--lah, fo+o", "b_lah_foo"),
    ("s(*&(*&al62", "sal62"),
])
def test_sanitize_id(input, output):
    assert sanitize_id(input) == output
