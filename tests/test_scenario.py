import importlib

import pytest


@pytest.fixture
def example_module(examples, monkeypatch):
    """Returns the example module."""

    def pick_module(example, name):
        monkeypatch.syspath_prepend(examples[example])
        return importlib.import_module(name)

    return pick_module


def test_location_app_scenario(example_module):
    location_module = example_module("location_hierarchy", "location_app")
    app_class = location_module.Application


def test_tmp_path(fair, shared_cluster_tmp):
    assert shared_cluster_tmp.exists()
