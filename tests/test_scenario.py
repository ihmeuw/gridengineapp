import importlib

import pytest


@pytest.fixture
def location_app(examples, monkeypatch):
    """Returns the example module."""
    monkeypatch.syspath_prepend(examples["location_hierarchy"])
    return importlib.import_module("location_app")


def test_location_app_scenario(location_app):
    AppClass = location_app.Application
