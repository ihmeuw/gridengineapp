import pytest

from gridengineapp.run_grid_app import sanitize_id, format_memory


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


@pytest.mark.parametrize("mem_gb,mem_str", [
    (1, "1GB"),
    (17, "17GB"),
    (1.5, "1536MB"),
    (0, "128MB"),
    (0.3583984375, "367MB"),
])
def test_format_memory(mem_gb, mem_str):
    assert format_memory(mem_gb) == mem_str
