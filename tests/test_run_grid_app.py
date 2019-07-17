import pytest

from gridengineapp.run_grid_app import sanitize_id, format_memory


@pytest.mark.parametrize("input,output", [
    ("myname", "myname"),
    ("sal62", "sal62"),
    (str(("hi", 7)), "hi_7"),  # using a tuple is a common case.
    ("blah,foo", "blah_foo"),
    ("blah, foo", "blah_foo"),
    ("blah, fo+o", "blah_foo"),
    ("b--lah, fo+o", "b_lah_foo"),
    ("s(*&(*&al62", "sal62"),
])
def test_sanitize_id(input, output):
    assert sanitize_id(input) == output


@pytest.mark.parametrize("mem_gb,mem_str", [
    (1, "1G"),
    (17, "17G"),
    (1.5, "1536M"),
    (0, "128M"),
    (0.3583984375, "367M"),
])
def test_format_memory(mem_gb, mem_str):
    assert format_memory(mem_gb) == mem_str
