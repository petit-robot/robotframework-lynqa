"""Pytest configuration for tests."""

from pylynqa.models import TestData, TestRunContext


def pytest_configure(config):
    """Pytest configuration tests."""
    # Prevent pytest from collecting these model classes as test suites
    # (their names start with "Test" but they are domain objects, not test cases).
    TestData.__test__ = False  # ty: ignore[unresolved-attribute]
    TestRunContext.__test__ = False  # ty: ignore[unresolved-attribute]
