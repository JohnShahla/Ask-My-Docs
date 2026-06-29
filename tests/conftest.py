"""Skip integration tests unless RUN_INTEGRATION is set.

Integration tests touch Chroma and download a local embedding model, so they're
opt-in. CI runs `pytest -m "not integration"`; locally, set RUN_INTEGRATION=1 to
exercise the full ingest → query path.
"""

import os

import pytest


def pytest_collection_modifyitems(config, items):
    if os.getenv("RUN_INTEGRATION"):
        return
    skip = pytest.mark.skip(reason="set RUN_INTEGRATION=1 to run integration tests")
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip)
