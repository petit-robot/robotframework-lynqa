"""Pytest configuration for tests."""

import base64
from pathlib import Path

import pytest
from pylynqa.models import TestData, TestRunContext

SCREENSHOT_PNG_FILE = Path(__file__).parent / "data_set" / "screenshot.png"


def pytest_configure(config):
    """Pytest configuration tests."""
    # Prevent pytest from collecting these model classes as test suites
    # (their names start with "Test" but they are domain objects, not test cases).
    TestData.__test__ = False  # ty: ignore[unresolved-attribute]
    TestRunContext.__test__ = False  # ty: ignore[unresolved-attribute]


@pytest.fixture
def screenshot_base64():
    """Return the sample screenshot as base64-encoded PNG data.

    Shared by the library integration tests and the reporter unit tests as the fake payload returned by the mocked
    ``get_screenshot`` client call.

    :returns: Base64-encoded contents of the sample PNG fixture.
    """
    return base64.b64encode(SCREENSHOT_PNG_FILE.read_bytes()).decode()
