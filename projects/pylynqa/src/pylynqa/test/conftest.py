"""Pytest configuration for pylynqa tests."""

from pylynqa.models import TestData, TestRunContext, TestRunsFilter


def pytest_configure(config):
    """Pytest configuration for pylynqa tests."""
    # Prevent pytest from collecting these model classes as test suites
    # (their names start with "Test" but they are domain objects, not test cases).
    TestData.__test__ = False  # ty: ignore[unresolved-attribute]
    TestRunContext.__test__ = False  # ty: ignore[unresolved-attribute]
    TestRunsFilter.__test__ = False  # ty: ignore[unresolved-attribute]
