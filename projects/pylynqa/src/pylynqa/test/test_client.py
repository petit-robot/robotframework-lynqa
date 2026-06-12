"""Unit tests for :mod:`pylynqa.client`."""
# ruff: file-ignore[undocumented-public-class,no-self-use]

import base64
from pathlib import Path

import pytest
from responses import matchers

from pylynqa import CreateAttachment, CreateTestStep, LynqaClient, TestData, TestRunContext, TestRunsFilter, TextualData
from pylynqa.client import (
    ENDPOINT_ACCOUNT_CREDIT_LEDGER,
    ENDPOINT_ACCOUNT_CREDITS,
    ENDPOINT_ACCOUNT_PURCHASES,
    ENDPOINT_HEALTH_LIVE,
    ENDPOINT_HEALTH_READY,
    ENDPOINT_TEST_RUNS,
    ENDPOINT_TEST_RUNS_GHERKIN,
    ENDPOINT_TEST_RUNS_QUERY,
    ENDPOINT_TEST_RUNS_STOP,
)
from pylynqa.test import API_KEY, assert_raises_on_error, body, url
from pylynqa.test.data_set import (
    CREDIT_LEDGER_ENTRIES,
    STEP_REPORT,
    TEST_RUN,
    TEST_RUN_FULL_STATUS,
    TEST_RUN_ID,
    TEST_RUN_ID_2,
    TEST_RUN_STATUS,
    TEST_RUNS,
)


@pytest.fixture
def client():
    """Return a :class:`LynqaClient` configured for testing."""
    return LynqaClient(api_key=API_KEY)


class TestAuthentication:
    def test_api_key_sent_in_header(self, client, responses):
        """Test."""
        # Arrange / Assert
        responses.add(
            responses.GET,
            url(ENDPOINT_ACCOUNT_CREDITS),
            json=10,
            match=[matchers.header_matcher({"x-api-key": API_KEY})],
        )

        # Act
        client.get_test_execution_credits()


class TestHealth:
    def test_health_live(self, client, responses):
        """Test."""
        # Arrange
        status_ok = {"status": "ok"}
        responses.add(responses.GET, url(ENDPOINT_HEALTH_LIVE), json=status_ok)

        # Act
        result = client.health_live()

        # Assert
        assert result == status_ok

    def test_health_ready(self, client, responses):
        """Test."""
        # Arrange
        status_ready = {"status": "ready"}
        responses.add(responses.GET, url(ENDPOINT_HEALTH_READY), json=status_ready)

        # Act
        result = client.health_ready()

        # Assert
        assert result == status_ready


class TestAddTestRun:
    RUN_ID = "mf4zz9945nwbofv81shozwb5"

    def test_sends_required_fields(self, client, responses):
        """Test."""
        # Arrange / Assert
        responses.add(
            responses.POST,
            url(ENDPOINT_TEST_RUNS),
            json=TEST_RUN_ID,
            status=201,
            match=[
                matchers.json_params_matcher(
                    {
                        "url": "https://example.com",
                        "steps": [{"action": "Click login"}],
                    }
                )
            ],
        )

        # Act
        test_run_id = client.add_test_run(
            url="https://example.com",
            steps=[CreateTestStep(action="Click login")],
        )

        # Assert
        assert test_run_id == TEST_RUN_ID

    def test_sends_optional_fields(self, client, responses):
        """Test."""
        # Arrange
        responses.add(responses.POST, url(ENDPOINT_TEST_RUNS), json=TEST_RUN_ID, status=201)

        # Act
        test_run_id = client.add_test_run(
            url="https://example.com",
            name="My test",
            steps=[
                CreateTestStep(
                    action="Click login",
                    expected_result="User is logged in",
                    attachments=[CreateAttachment(name="step.txt", data="data:text/plain;base64,SmFuZQo=")],
                )
            ],
            context=TestRunContext(
                client_language="en-US",
                secrets=[TestData(name="password", value="s3cr3t")],
            ),
            guidance=[TextualData(text="The user is between 18 and 49")],
            attachments=[CreateAttachment(name="file.txt", data="data:text/plain;base64,SmFuZQo=")],
        )

        # Assert
        assert test_run_id == TEST_RUN_ID
        assert body(responses, 0) == {
            "url": "https://example.com",
            "name": "My test",
            "steps": [
                {
                    "action": "Click login",
                    "expectedResult": "User is logged in",
                    "attachments": [{"name": "step.txt", "data": "data:text/plain;base64,SmFuZQo="}],
                }
            ],
            "context": {
                "clientLanguage": "en-US",
                "secrets": [{"name": "password", "value": "s3cr3t"}],
            },
            "guidance": [{"text": "The user is between 18 and 49"}],
            "attachments": [{"name": "file.txt", "data": "data:text/plain;base64,SmFuZQo="}],
        }

    @pytest.mark.parametrize(
        ("status_code", "error"),
        [
            (400, "Test is malformed"),
            (401, "Authentication failed"),
            (403, "Not enough credits"),
            (422, "URL is not safe"),
            (429, "Too many requests"),
        ],
    )
    def test_raises_on_error(self, client, responses, status_code, error):
        """Test."""
        assert_raises_on_error(
            responses,
            "POST",
            url(ENDPOINT_TEST_RUNS),
            lambda: client.add_test_run(url="https://example.com", steps=[]),
            status_code,
            error,
        )


class TestAddGherkinTestRun:
    RUN_ID = "mf4zz9945nwbofv81shozwb5"
    SCENARIO = "Given I am on the login page\nWhen I submit valid credentials\nThen I am logged in"

    def test_sends_required_fields(self, client, responses):
        """Test."""
        # Arrange / Assert
        responses.add(
            responses.POST,
            url(ENDPOINT_TEST_RUNS_GHERKIN),
            json=TEST_RUN_ID,
            status=201,
            match=[
                matchers.json_params_matcher(
                    {
                        "url": "https://example.com",
                        "scenario": self.SCENARIO,
                    }
                )
            ],
        )

        # Act
        run_id = client.add_gherkin_test_run(
            url="https://example.com",
            scenario=self.SCENARIO,
        )

        # Assert
        assert run_id == TEST_RUN_ID

    def test_sends_optional_fields(self, client, responses):
        """Test."""
        # Arrange
        responses.add(responses.POST, url(ENDPOINT_TEST_RUNS_GHERKIN), json=TEST_RUN_ID, status=201)

        # Act
        run_id = client.add_gherkin_test_run(
            url="https://example.com",
            scenario=self.SCENARIO,
            name="My Gherkin test",
            context=TestRunContext(
                client_language="en-US",
                secrets=[TestData(name="password", value="s3cr3t")],
            ),
            guidance=[TextualData(text="The user is between 18 and 49")],
            attachments=[CreateAttachment(name="file.txt", data="data:text/plain;base64,SmFuZQo=")],
        )

        # Assert
        assert run_id == TEST_RUN_ID
        assert body(responses, 0) == {
            "url": "https://example.com",
            "scenario": self.SCENARIO,
            "name": "My Gherkin test",
            "context": {
                "clientLanguage": "en-US",
                "secrets": [{"name": "password", "value": "s3cr3t"}],
            },
            "guidance": [{"text": "The user is between 18 and 49"}],
            "attachments": [{"name": "file.txt", "data": "data:text/plain;base64,SmFuZQo="}],
        }

    @pytest.mark.parametrize(
        ("status_code", "error"),
        [
            (400, "Test is malformed"),
            (401, "Authentication failed"),
            (403, "Not enough credits"),
            (422, "URL is not safe"),
            (429, "Too many requests"),
        ],
    )
    def test_raises_on_error(self, client, responses, status_code, error):
        """Test."""
        assert_raises_on_error(
            responses,
            "POST",
            url(ENDPOINT_TEST_RUNS_GHERKIN),
            lambda: client.add_gherkin_test_run(url="https://example.com", scenario=self.SCENARIO),
            status_code,
            error,
        )


class TestGetTestRun:
    def test_returns_test_run(self, client, responses):
        """Test."""
        # Arrange
        responses.add(responses.GET, url(f"{ENDPOINT_TEST_RUNS}/{TEST_RUN_ID}"), json=TEST_RUN)

        # Act
        result = client.get_test_run(TEST_RUN_ID)

        # Assert
        assert result == TEST_RUN

    @pytest.mark.parametrize(
        ("status_code", "error"),
        [
            (401, "Authentication failed"),
            (404, "Not found"),
            (410, "Test run expired"),
            (429, "Too many requests"),
        ],
    )
    def test_raises_on_error(self, client, responses, status_code, error):
        """Test."""
        assert_raises_on_error(
            responses,
            "GET",
            url(f"{ENDPOINT_TEST_RUNS}/{TEST_RUN_ID}"),
            lambda: client.get_test_run(TEST_RUN_ID),
            status_code,
            error,
        )


class TestDeleteTestRun:
    def test_delete(self, client, responses):
        """Test."""
        # Arrange
        resp = responses.add(responses.DELETE, url(f"{ENDPOINT_TEST_RUNS}/{TEST_RUN_ID}"), status=204)

        # Act
        client.delete_test_run(TEST_RUN_ID)

        # Assert
        assert resp.call_count == 1

    @pytest.mark.parametrize(
        ("status_code", "error"),
        [
            (401, "Authentication failed"),
            (404, "Test run not found"),
            (429, "Too many requests"),
        ],
    )
    def test_raises_on_error(self, client, responses, status_code, error):
        """Test."""
        assert_raises_on_error(
            responses,
            "DELETE",
            url(f"{ENDPOINT_TEST_RUNS}/{TEST_RUN_ID}"),
            lambda: client.delete_test_run(TEST_RUN_ID),
            status_code,
            error,
        )


class TestGetTestRunStatus:
    def test_returns_status(self, client, responses):
        """Test."""
        # Arrange
        responses.add(responses.GET, url(f"{ENDPOINT_TEST_RUNS}/{TEST_RUN_ID}/status"), json=TEST_RUN_STATUS)

        # Act
        result = client.get_test_run_status(TEST_RUN_ID)

        # Assert
        assert result["status"] == "running"

    @pytest.mark.parametrize(
        ("status_code", "error"),
        [
            (401, "Authentication failed"),
            (404, "Test run not found"),
            (410, "Test run expired"),
            (429, "Too many requests"),
        ],
    )
    def test_raises_on_error(self, client, responses, status_code, error):
        """Test."""
        assert_raises_on_error(
            responses,
            "GET",
            url(f"{ENDPOINT_TEST_RUNS}/{TEST_RUN_ID}/status"),
            lambda: client.get_test_run_status(TEST_RUN_ID),
            status_code,
            error,
        )


class TestGetTestRunFullStatus:
    def test_returns_full_status(self, client, responses):
        """Test."""
        # Arrange
        responses.add(responses.GET, url(f"{ENDPOINT_TEST_RUNS}/{TEST_RUN_ID}/fullStatus"), json=TEST_RUN_FULL_STATUS)

        # Act
        result = client.get_test_run_full_status(TEST_RUN_ID)

        # Assert
        assert result["status"] == "running"
        assert result["stepStatuses"][0]["status"] == "success"

    @pytest.mark.parametrize(
        ("status_code", "error"),
        [
            (401, "Authentication failed"),
            (404, "Test run not found"),
            (410, "Test run expired"),
            (429, "Too many requests"),
        ],
    )
    def test_raises_on_error(self, client, responses, status_code, error):
        """Test."""
        assert_raises_on_error(
            responses,
            "GET",
            url(f"{ENDPOINT_TEST_RUNS}/{TEST_RUN_ID}/fullStatus"),
            lambda: client.get_test_run_full_status(TEST_RUN_ID),
            status_code,
            error,
        )


class TestStopTestRuns:
    def test_returns_stopped_ids(self, client, responses):
        """Test."""
        # Arrange
        test_run_id_list = [TEST_RUN_ID, TEST_RUN_ID_2]
        responses.add(
            responses.POST,
            url(ENDPOINT_TEST_RUNS_STOP),
            json={"stoppedTestRunIds": test_run_id_list},
            status=202,
        )

        # Act
        result = client.stop_test_runs(test_run_id_list)

        # Assert
        assert result["stoppedTestRunIds"] == test_run_id_list

    def test_sends_test_run_ids(self, client, responses):
        """Test."""
        # Arrange / Assert
        responses.add(
            responses.POST,
            url(ENDPOINT_TEST_RUNS_STOP),
            json={"stoppedTestRunIds": []},
            status=202,
            match=[matchers.json_params_matcher({"testRunIds": [10, 20]})],
        )

        # Act
        client.stop_test_runs([10, 20])

    @pytest.mark.parametrize(
        ("status_code", "error"),
        [
            (400, "Body is malformed"),
            (401, "Authentication failed"),
            (429, "Too many requests"),
        ],
    )
    def test_raises_on_error(self, client, responses, status_code, error):
        """Test."""
        assert_raises_on_error(
            responses,
            "POST",
            url(ENDPOINT_TEST_RUNS_STOP),
            lambda: client.stop_test_runs([TEST_RUN_ID]),
            status_code,
            error,
        )


class TestQueryTestRuns:
    def test_returns_paginated_results(self, client, responses):
        """Test."""
        # Arrange
        limit = 2
        responses.add(responses.POST, url(ENDPOINT_TEST_RUNS_QUERY), json=TEST_RUNS)

        # Act
        result = client.query_test_runs(0, 2, TestRunsFilter(statuses=["failed"]))

        # Assert
        assert len(result["testRuns"]) == len(TEST_RUNS)
        assert result["nextCursor"] == limit

    @pytest.mark.parametrize(
        ("status_code", "error"),
        [
            (400, "Query is malformed"),
            (401, "Authentication failed"),
            (429, "Too many requests"),
        ],
    )
    def test_raises_on_error(self, client, responses, status_code, error):
        """Test."""
        assert_raises_on_error(
            responses,
            "POST",
            url(ENDPOINT_TEST_RUNS_QUERY),
            client.query_test_runs,
            status_code,
            error,
        )


class TestGetTestRunStepStatus:
    def test_returns_step_report(self, client, responses):
        """Test."""
        # Arrange
        responses.add(responses.GET, url(f"{ENDPOINT_TEST_RUNS}/{TEST_RUN_ID}/testSteps/0"), json=STEP_REPORT)

        # Act
        result = client.get_test_run_step_status(TEST_RUN_ID, 0)

        # Assert
        assert result["status"] == "failed"
        assert result["commands"][0]["name"] == "fill"

    @pytest.mark.parametrize(
        ("status_code", "error"),
        [
            (401, "Authentication failed"),
            (404, "Test run step not found"),
            (429, "Too many requests"),
        ],
    )
    def test_raises_on_error(self, client, responses, status_code, error):
        """Test."""
        assert_raises_on_error(
            responses,
            "GET",
            url(f"{ENDPOINT_TEST_RUNS}/{TEST_RUN_ID}/testSteps/0"),
            lambda: client.get_test_run_step_status(TEST_RUN_ID, 0),
            status_code,
            error,
        )


class TestGetScreenshot:
    def test_returns_base64_data(self, client, responses):
        """Test."""
        # Arrange
        screenshot_id = "4b111ba4-c236-4770-67bf-0f17d0230e47"
        screenshot = Path(__file__).parent / "screenshot.png"
        screenshot_base64 = base64.b64encode(screenshot.open("rb").read()).decode()
        responses.add(
            responses.GET,
            url(f"{ENDPOINT_TEST_RUNS}/{TEST_RUN_ID}/screenshots/{screenshot_id}"),
            json={"data": screenshot_base64},
        )

        # Act
        result = client.get_screenshot(TEST_RUN_ID, screenshot_id)

        # Assert
        assert (
            result == "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        )

    @pytest.mark.parametrize(
        ("status_code", "error"),
        [
            (401, "Authentication failed"),
            (404, "Screenshot not found"),
            (410, "Test run expired"),
            (429, "Too many requests"),
        ],
    )
    def test_raises_on_error(self, client, responses, status_code, error):
        """Test."""
        assert_raises_on_error(
            responses,
            "GET",
            url(f"{ENDPOINT_TEST_RUNS}/{TEST_RUN_ID}/screenshots/abc-123"),
            lambda: client.get_screenshot(TEST_RUN_ID, "abc-123"),
            status_code,
            error,
        )


class TestAccount:
    def test_get_test_execution_credits(self, client, responses):
        """Test."""
        # Arrange
        credits_amount = 100
        responses.add(responses.GET, url(ENDPOINT_ACCOUNT_CREDITS), json=credits_amount)

        # Act
        result = client.get_test_execution_credits()

        # Assert
        assert result == credits_amount

    @pytest.mark.parametrize(
        ("status_code", "error"),
        [
            (401, "Authentication failed"),
            (429, "Too many requests"),
        ],
    )
    def test_get_test_execution_credits_raises_on_error(self, client, responses, status_code, error):
        """Test."""
        assert_raises_on_error(
            responses,
            "GET",
            url(ENDPOINT_ACCOUNT_CREDITS),
            client.get_test_execution_credits,
            status_code,
            error,
        )

    def test_get_purchases(self, client, responses):
        """Test."""
        # Arrange
        payload = [{"id": 1, "amount": 100}]  # Need to be confirmed
        responses.add(responses.GET, url(ENDPOINT_ACCOUNT_PURCHASES), json=payload)

        # Act
        result = client.get_purchases()

        # Assert
        assert result == payload

    @pytest.mark.parametrize(
        ("status_code", "error"),
        [
            (401, "Authentication failed"),
            (429, "Too many requests"),
        ],
    )
    def test_get_purchases_raises_on_error(self, client, responses, status_code, error):
        """Test."""
        assert_raises_on_error(
            responses,
            "GET",
            url(ENDPOINT_ACCOUNT_PURCHASES),
            client.get_purchases,
            status_code,
            error,
        )

    def test_get_credit_ledger(self, client, responses):
        """Test."""
        # Arrange
        responses.add(responses.GET, url(ENDPOINT_ACCOUNT_CREDIT_LEDGER), json=CREDIT_LEDGER_ENTRIES)

        # Act
        result = client.get_credit_ledger()

        # Assert
        assert result == CREDIT_LEDGER_ENTRIES

    @pytest.mark.parametrize(
        ("status_code", "error"),
        [
            (401, "Authentication failed"),
            (429, "Too many requests"),
        ],
    )
    def test_get_credit_ledger_raises_on_error(self, client, responses, status_code, error):
        """Test."""
        assert_raises_on_error(
            responses,
            "GET",
            url(ENDPOINT_ACCOUNT_CREDIT_LEDGER),
            client.get_credit_ledger,
            status_code,
            error,
        )
