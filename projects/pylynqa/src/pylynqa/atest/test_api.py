"""Acceptance tests for the Lynqa API — no mocking, real HTTP calls.

Requires the environment variable ``LYNQA_API_KEY`` to be set.

Run with::

    LYNQA_API_KEY=lq_live_xxx pytest projects/pylynqa/src/pylynqa/atest -v
"""

# ruff: file-ignore[undocumented-public-method,no-self-use]
import os
import time
from datetime import datetime

import pylynqa
import pytest
import responses
from pylynqa import LynqaClient, TestRunsFilter, TimePeriod

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

POLL_TIMEOUT_S = 300
TERMINAL_STATUSES = {"success", "failed", "error", "stopped", "not_run"}

TEST_RUN_NAME = f"Automatic test — Google search for lynqa - {datetime.now().isoformat()}"
GHERKIN_SCENARIO = (
    "Given go to https://www.google.com/\n"
    "When I look at the search input\n"
    "Then the search input exists\n"
    "When I search for 'lynqa'\n"
    "Then several results are displayed"
    "Then the first results display 'Smartesting'"
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def client() -> LynqaClient:
    """Instantiate a LynqaClient object."""
    api_key = os.environ.get("LYNQA_API_KEY")
    if not api_key:
        pytest.skip("LYNQA_API_KEY environment variable is not set")  # ty: ignore[too-many-positional-arguments]
    return LynqaClient(api_key=api_key)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _wait_for_completion(client: LynqaClient, run_id: str) -> None:
    """Poll status until the run reaches a terminal state or the timeout expires."""
    deadline = time.monotonic() + POLL_TIMEOUT_S
    while time.monotonic() < deadline:
        result = client.get_test_run_status(run_id)
        if result["status"] in TERMINAL_STATUSES:
            return
        time.sleep(5)
    pytest.fail(f"Test run {run_id!r} did not complete within {POLL_TIMEOUT_S}s")  # ty: ignore[invalid-argument-type]
    return None


# ---------------------------------------------------------------------------
# Test scenario
# ---------------------------------------------------------------------------


class TestApiScenario:
    """End-to-end scenario exercising all major API operations in order."""

    test_run_id: str = ""

    _INDEPENDENT_TESTS = (
        "test_health_live",
        "test_health_ready",
        "test_get_account_credits",
        "test_get_purchases",
        "test_get_credit_ledger",
        "test_create_gherkin_test_run",
    )

    @pytest.fixture(autouse=True)  # ruff: ignore[pytest-fixture-autouse]
    def setup(self, request):
        """Set up all tests."""
        # Disable HTTP mocking for all requests to the real API base URL.
        responses.add_passthru(pylynqa.BASE_URL)
        # Skip certain tests if test run not created
        if request.node.name not in self._INDEPENDENT_TESTS and not TestApiScenario.test_run_id:
            pytest.skip("skipped: test_create_gherkin_test_run did not produce a test_run_id")  # ty: ignore[too-many-positional-arguments]

    def test_health_live(self, client):
        # Act
        result = client.health_live()
        # Assert
        assert result["status"] == "ok"

    def test_health_ready(self, client):
        # Act
        result = client.health_ready()
        # Assert
        assert result["ready"]

    def test_get_account_credits(self, client):
        # Act
        credits = client.get_test_execution_credits()
        # Assert
        assert isinstance(credits, int)
        assert credits >= 0

    def test_get_purchases(self, client):
        # Act
        purchases = client.get_purchases()
        # Assert
        assert isinstance(purchases, list)

    def test_get_credit_ledger(self, client):
        # Act
        ledger = client.get_credit_ledger()
        # Assert
        assert isinstance(ledger, list)
        assert len(ledger) > 0
        assert ledger[0]["balanceAfter"] != 0, "Should have at least one credit ledger"

    def test_create_gherkin_test_run(self, client):
        # Act
        TestApiScenario.test_run_id = client.add_gherkin_test_run(
            url="https://www.google.com/",
            scenario=GHERKIN_SCENARIO,
            name=TEST_RUN_NAME,
        )
        # Assert
        assert TestApiScenario.test_run_id is not None
        if not isinstance(TestApiScenario.test_run_id, str):
            pytest.warns(UserWarning, match="test_run_id is not a str")
        else:
            assert len(TestApiScenario.test_run_id) > 0

    def test_get_test_run_status(self, client):
        # Act
        result = client.get_test_run_status(TestApiScenario.test_run_id)
        # Assert
        assert "status" in result
        assert result["status"] in {"waiting", "running"} | TERMINAL_STATUSES

    def test_get_test_run_full_status(self, client):
        # Arrange
        _wait_for_completion(client, TestApiScenario.test_run_id)
        # Act
        result = client.get_test_run_full_status(TestApiScenario.test_run_id)
        # Assert
        assert "status" in result
        assert result["status"] in TERMINAL_STATUSES
        assert "stepStatuses" in result
        assert "steps" in result
        assert len(result["stepStatuses"]) == len(result["steps"])
        assert len(result["stepStatuses"]) > 0
        assert result["type"] == "gherkin"

    def test_get_test_run(self, client):
        # Act
        result = client.get_test_run(TestApiScenario.test_run_id)
        # Assert
        assert result["name"] == TEST_RUN_NAME
        assert result["url"] == "https://www.google.com/"
        assert result["type"] == "gherkin"
        assert "steps" in result

    def test_get_step_info(self, client):
        # Arrange
        status_result = client.get_test_run_full_status(TestApiScenario.test_run_id)
        if not status_result.get("stepStatuses"):
            pytest.skip("No steps available in full status")  # ty: ignore[too-many-positional-arguments]
        # Act
        result = client.get_test_run_step_status(TestApiScenario.test_run_id, 0)
        # Assert
        assert "status" in result
        assert "commands" in result
        assert "assertionsReport" in result

    def test_get_screenshot_info(self, client):
        # Arrange
        status = client.get_test_run_status(TestApiScenario.test_run_id)
        screenshot_id = status.get("initialReport", {}).get("screenshot")
        if not screenshot_id:
            pytest.skip("No initial screenshot available")  # ty: ignore[too-many-positional-arguments]
        # Act
        data = client.get_screenshot(TestApiScenario.test_run_id, screenshot_id)
        # Assert
        assert isinstance(data, str)
        assert len(data) > 0

    def test_query_test_runs(self, client):
        # Act
        result = client.query_test_runs(filters=TestRunsFilter(relative_period=TimePeriod(count=5, unit="m")))
        # Assert
        assert "testRuns" in result
        assert len(result["testRuns"]) > 0
        if not isinstance(TestApiScenario.test_run_id, str):
            pytest.warns(UserWarning, match="test_run_id is not a str")
        assert result["testRuns"][-1].get("id", 0) == str(
            TestApiScenario.test_run_id
        )  # Remove str casting when API ready

    def test_stop_test_runs(self, client):
        # Act
        result = client.stop_test_runs([TestApiScenario.test_run_id])
        # Assert
        assert "stoppedTestRunIds" in result
        assert isinstance(result["stoppedTestRunIds"], list)

    def test_delete_test_run(self, client):
        # Act
        client.delete_test_run(TestApiScenario.test_run_id)
        # Assert
        with pytest.raises(pylynqa.LynqaClientError):
            client.get_test_run_status(TestApiScenario.test_run_id)
