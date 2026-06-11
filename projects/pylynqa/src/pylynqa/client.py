"""Lynqa API Client.

Python client for the `Lynqa API <https://api.lynqa.smartesting.com/api-docs>`_.

Lynqa is a manual test execution service. This module provides a thin, synchronous wrapper around the REST API, covering
test run management, step inspection, screenshot retrieval, and account operations.

**Authentication**

Every request is authenticated with an API key passed in the ``x-api-key`` HTTP header. Keys are created at
https://my.lynqa.smartesting.com/integration.

**Quick start**:

::

    from lynqa import CreateTestStep, LynqaClient

    client = LynqaClient(api_key="your-api-key")

    run_id = client.add_test_run(
        url="https://example.com",
        steps=[
            CreateTestStep(
                action='Click on the "Login" button',
                expected_result="The user is logged in",
            ),
        ],
        name="Smoke - login",
    )

    status = client.get_test_run_status(run_id)
    print(status["status"])  # e.g. "running"
"""

from __future__ import annotations

import requests

from pylynqa.models import (
    CreateAttachment,
    CreateTestStep,
    LynqaClientError,
    TestRunContext,
    TestRunsFilter,
    TextualData,
)

DEFAULT_CONSUMER = "petit-robot:pylynqa"

BASE_URL = "https://api.lynqa.smartesting.com"

ENDPOINT_HEALTH_LIVE = "/health/live"
ENDPOINT_HEALTH_READY = "/health/ready"
ENDPOINT_TEST_RUNS = "/testRuns"
ENDPOINT_TEST_RUNS_GHERKIN = "/testRuns/gherkin"
ENDPOINT_TEST_RUNS_STOP = "/testRuns/stop"
ENDPOINT_TEST_RUNS_QUERY = "/testRuns/query"
ENDPOINT_ACCOUNT_CREDITS = "/account/credits"
ENDPOINT_ACCOUNT_PURCHASES = "/account/purchases"
ENDPOINT_ACCOUNT_CREDIT_LEDGER = "/account/creditLedger"


class LynqaClient:
    """Synchronous client for the Lynqa REST API.

    Wraps every API endpoint in a typed Python method. All network calls use a shared :class:`requests.Session` so that
    TCP connections are reused across requests.

    :param api_key: Lynqa API key.
    :param base_url: Base URL of the API. Defaults to the production server ``https://api.lynqa.smartesting.com``.
        Override for self-hosted or staging environments.

    :raises LynqaClientError: On any non-2xx response from the API.

    Example:
    ::

        client = LynqaClient(api_key="lq_live_xxxxxxxxxxxx")
        print(client.get_test_execution_credits())  # 410

    """

    def __init__(self, api_key: str, base_url: str = BASE_URL) -> None:
        """Initialize the client with the given API key and base URL.

        :param api_key: Lynqa API key obtained from
        :param base_url: Base URL of the API. Defaults to the production
        """
        self._session = requests.Session()
        self._session.headers.update({"x-api-key": api_key})
        self._base_url = base_url.rstrip("/")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        """Send an authenticated HTTP request.

        :param method: HTTP verb (``'GET'``, ``'POST'``, ``'DELETE'``, …).
        :param path: URL path relative to the base URL, e.g. ``'/testRuns'``.
        :param kwargs: Extra keyword arguments forwarded to :meth:`requests.Session.request`.

        :returns: The HTTP response object.

        :raises LynqaClientError: If the response status code indicates an error.
        """
        url = f"{self._base_url}{path}"
        response = self._session.request(method, url, **kwargs)
        if not response.ok:
            try:
                body = response.json()
                error = body.get("error", "")
                message = body.get("message", "")
            except Exception:
                error = response.text
                message = ""
            raise LynqaClientError(response.status_code, error=error, message=message)
        return response

    # ------------------------------------------------------------------
    # Health
    # ------------------------------------------------------------------

    def health_live(self) -> dict:
        """Check whether the API service is alive.

        Corresponds to ``GET /health/live``.

        :returns: Server response body.
        """
        return self._request("GET", ENDPOINT_HEALTH_LIVE).json()

    def health_ready(self) -> dict:
        """Check whether the API service is ready to accept requests.

        Corresponds to ``GET /health/ready``.

        :returns: Server response body.
        """
        return self._request("GET", ENDPOINT_HEALTH_READY).json()

    # ------------------------------------------------------------------
    # Test Runs
    # ------------------------------------------------------------------

    def add_test_run(  # noqa: PLR0913
        self,
        url: str,
        steps: list[CreateTestStep],
        *,
        name: str | None = None,
        context: TestRunContext | None = None,
        guidance: list[TextualData] | None = None,
        attachments: list[CreateAttachment] | None = None,
        consumer: str = DEFAULT_CONSUMER,
    ) -> str:
        """Execute a manual test run.

        Corresponds to ``POST /testRuns``.

        :param url: URL of the system under test, e.g. ``'https://my-app.example.com'``.
        :param steps: Ordered list of test steps to execute.
        :param name: Optional human-readable name for this run.
        :param context: Optional locale and secrets context.
        :param guidance: Optional global guidance hints for the agent.
        :param attachments: Optional files attached to the test run (base64-encoded).
        :param consumer: Value for the required ``x-api-consumer`` header. Use a string that identifies the calling
            system, e.g. ``'jira:my-instance.atlassian.net'``.

        :returns: The ID assigned to the new test run.

        :raises LynqaClientError: On API errors (400, 401, 403, 422, 429).

        Example:
        ::

            run_id = client.add_test_run(
                url="https://example.com",
                steps=[
                    CreateTestStep(
                        action='Fill in the username field with "admin"',
                        expected_result="The username field shows 'admin'",
                    ),
                    CreateTestStep(action='Click on "Submit"'),
                ],
                name="Login - happy path",
            )

        """
        body: dict = {"url": url, "steps": [s.to_dict() for s in steps]}
        if name is not None:
            body["name"] = name
        if context is not None:
            body["context"] = context.to_dict()
        if guidance:
            body["guidance"] = [g.to_dict() for g in guidance]
        if attachments:
            body["attachments"] = [a.to_dict() for a in attachments]

        return self._request(
            "POST",
            ENDPOINT_TEST_RUNS,
            json=body,
            headers={"x-api-consumer": consumer},
        ).json()

    def add_gherkin_test_run(  # noqa: PLR0913
        self,
        url: str,
        scenario: str,
        *,
        name: str | None = None,
        context: TestRunContext | None = None,
        guidance: list[TextualData] | None = None,
        attachments: list[CreateAttachment] | None = None,
        consumer: str = DEFAULT_CONSUMER,
    ) -> str:
        r"""Execute a Gherkin (BDD) test run.

        Corresponds to ``POST /testRuns/gherkin``.

        :param url: URL of the system under test.
        :param scenario: Full Gherkin scenario text, including ``Given``, ``When``, and ``Then`` steps.
        :param name: Optional human-readable name for this run.
        :param context: Optional locale and secrets context.
        :param guidance: Optional global guidance hints for the agent.
        :param attachments: Optional files attached to the test run (base64-encoded).
        :param consumer: Value for the required ``x-api-consumer`` header.

        :returns: The ID assigned to the new test run.

        :raises LynqaClientError: On API errors (400, 401, 403, 422, 429).

        Example:
        ::

            run_id = client.add_gherkin_test_run(
                url="https://example.com",
                scenario=(
                    "Given the user is on the login page\\n"
                    "When the user enters valid credentials\\n"
                    "Then the user is redirected to the dashboard"
                ),
                name="Login - Gherkin",
            )

        """
        body: dict = {"url": url, "scenario": scenario}
        if name is not None:
            body["name"] = name
        if context is not None:
            body["context"] = context.to_dict()
        if guidance:
            body["guidance"] = [g.to_dict() for g in guidance]
        if attachments:
            body["attachments"] = [a.to_dict() for a in attachments]

        return self._request(
            "POST",
            ENDPOINT_TEST_RUNS_GHERKIN,
            json=body,
            headers={"x-api-consumer": consumer},
        ).json()

    def get_test_run(self, test_run_id: str) -> dict:
        """Retrieve a test run together with its steps.

        Corresponds to ``GET /testRuns/{testRunId}``.

        The response is either a *manual* test (``type`` = ``'manual'``) or a *Gherkin* test (``type`` = ``'gherkin'``).

        :param test_run_id: ID of the test run to retrieve.

        :returns: Test run dict including ``url``, ``type``, and ``steps``.

        :raises LynqaClientError: ``401`` authentication failed, ``404`` if not found, ``410`` if expired, ``429`` rate
            limit.
        """
        return self._request("GET", f"{ENDPOINT_TEST_RUNS}/{test_run_id}").json()

    def delete_test_run(self, test_run_id: str) -> None:
        """Delete a test run.

        Corresponds to ``DELETE /testRuns/{testRunId}``.

        :param test_run_id: ID of the test run to delete.

        :raises LynqaClientError: ``401`` authentication failed, ``404`` if not found, ``429`` rate limit.
        """
        self._request("DELETE", f"{ENDPOINT_TEST_RUNS}/{test_run_id}")

    def get_test_run_status(self, test_run_id: str) -> dict:
        """Get the overall status of a test run.

        Corresponds to ``GET /testRuns/{testRunId}/status``.

        The returned dict contains:

        - ``status`` *(str)* - one of ``waiting``, ``running``, ``success``, ``failed``, ``error``, ``stopped``,
          ``not_run``.
        - ``start`` / ``end`` *(str, ISO 8601)* - timing information.
        - ``expiration`` *(str, ISO 8601)* - when the run data will be purged.
        - ``initialReport`` *(dict)* - screenshot UUID captured before step 1, and an optional startup error (e.g.
          ``host_not_reachable``).

        :param test_run_id: ID of the test run.

        :returns: Status dict.

        :raises LynqaClientError: ``401`` authentication failed, ``404`` if not found, ``410`` if expired, ``429`` rate
            limit.
        """
        return self._request("GET", f"{ENDPOINT_TEST_RUNS}/{test_run_id}/status").json()

    def get_test_run_full_status(self, test_run_id: str) -> dict:
        """Get the full status of a test run, including per-step reports.

        Corresponds to ``GET /testRuns/{testRunId}/fullStatus``.

        Extends :meth:`get_test_run_status` with a ``stepStatuses`` list where each entry is a
        :class:`StepReport`-shaped dict containing the commands executed, timestamps, assertions report, verdict cause,
        or error.

        :param test_run_id: ID of the test run.

        :returns: Full status dict including ``stepStatuses``.

        :raises LynqaClientError: ``401`` authentication failed, ``404`` if not found, ``410`` if expired, ``429`` rate
            limit.
        """
        return self._request("GET", f"{ENDPOINT_TEST_RUNS}/{test_run_id}/fullStatus").json()

    def stop_test_runs(self, test_run_ids: list[str]) -> dict:
        """Request cancellation of one or more running test executions.

        Corresponds to ``POST /testRuns/stop``.

        :param test_run_ids: List of test run IDs to stop.

        :returns: Dict with ``stoppedTestRunIds`` - the IDs that were successfully scheduled for stopping.

        :raises LynqaClientError: ``400`` if body is malformed, ``401``, ``429``.

        Example:
        ::

            result = client.stop_test_runs([101, 102, 103])
            print(result["stoppedTestRunIds"])  # [101, 103]

        """
        return self._request("POST", ENDPOINT_TEST_RUNS_STOP, json={"testRunIds": test_run_ids}).json()

    def query_test_runs(
        self,
        cursor: int | None = None,
        limit: int | None = None,
        filters: TestRunsFilter | None = None,
    ) -> dict:
        """List paginated test runs matching the given filters.

        Corresponds to ``POST /testRuns/query``.

        :param cursor: Return runs starting from this cursor ID (from ``nextCursor`` in a previous response).
        :param limit: Maximum number of results to return.
        :param filters: Filter criteria. Pass a :class:`~pylynqa.models.TestRunsFilter` to narrow results by status,
            date range, API key, or run IDs. All fields are optional; omit to return all runs.

        :returns: Dict containing ``testRuns`` and an optional ``nextCursor`` for pagination.

        :raises LynqaClientError: ``400`` if the query is malformed, ``401`` authentication failed, ``429`` rate limit.

        Example:
        ::

            page = client.query_test_runs(
                filters=TestRunsFilter(
                    statuses=["failed"],
                    relative_period=TimePeriod(count=24, unit="h"),
                ),
                limit=50,
            )
            for run in page["testRuns"]:
                print(run["id"], run["status"])

        """
        params: dict = {}
        if cursor is not None:
            params["cursor"] = cursor
        if limit is not None:
            params["limit"] = limit
        body = filters.to_dict() if filters is not None else {}
        return self._request("POST", ENDPOINT_TEST_RUNS_QUERY, json=body, params=params).json()

    # ------------------------------------------------------------------
    # Test Steps
    # ------------------------------------------------------------------

    def get_test_run_step_status(self, test_run_id: str, step_index: int) -> dict:
        """Get the status report of a specific step within a test run.

        Corresponds to ``GET /testRuns/{testRunId}/testSteps/{stepIndex}``.

        The returned dict contains:

        - ``status`` *(str)* - step execution status.
        - ``commands`` *(list)* - browser commands executed during this step, each with ``name``, optional ``value``,
          ``htmlElement``, and ``screenshot`` (UUID).
        - ``start`` / ``end`` *(str, ISO 8601)* - present once the step has started / finished.
        - ``assertionsReport`` *(dict)* - present for ``success`` or ``failed`` steps; contains individual assertion
          checks and a screenshot UUID.
        - ``testVerdictCause`` *(str)* - human-readable failure reason, present when ``status`` is ``failed``.
        - ``error`` *(str)* - present when ``status`` is ``error``.

        :param test_run_id: ID of the test run.
        :param step_index: Zero-based index of the step to retrieve.

        :returns: Step report dict.

        :raises LynqaClientError: ``401`` authentication failed, ``404`` if not found, ``429`` rate limit.
        """
        return self._request("GET", f"{ENDPOINT_TEST_RUNS}/{test_run_id}/testSteps/{step_index}").json()

    # ------------------------------------------------------------------
    # Screenshots
    # ------------------------------------------------------------------

    def get_screenshot(self, test_run_id: str, screenshot_id: str) -> str:
        """Retrieve a screenshot as a base64-encoded string.

        Screenshot UUIDs are embedded in step reports and the initial report. Corresponds to ``GET
        /testRuns/{testRunId}/screenshots/{screenshotId}``.

        :param test_run_id: ID of the test run the screenshot belongs to.
        :param screenshot_id: UUID of the screenshot.

        :returns: Base64-encoded PNG data.

        :raises LynqaClientError: ``401`` authentication failed, ``404`` if not found, ``410`` if the run expired,
            ``429`` rate limit.

        Example:
        ::

            import base64

            data = client.get_screenshot(run_id, "4b111ba4-c236-4770-67bf-0f17d0230e47")
            with open("screenshot.png", "wb") as f:
                f.write(base64.b64decode(data))

        """
        return self._request("GET", f"{ENDPOINT_TEST_RUNS}/{test_run_id}/screenshots/{screenshot_id}").json()["data"]

    # ------------------------------------------------------------------
    # Account
    # ------------------------------------------------------------------

    def get_test_execution_credits(self) -> int:
        """Get the number of test execution credits available for this API key.

        Corresponds to ``GET /account/credits``.

        :returns: Remaining credit count.

        :raises LynqaClientError: ``401`` on authentication failure, ``429`` rate limit.
        """
        return self._request("GET", ENDPOINT_ACCOUNT_CREDITS).json()

    def get_purchases(self) -> list:
        """List credit purchase history for this API key.

        Corresponds to ``GET /account/purchases``.

        :returns: List of purchase records.

        :raises LynqaClientError: ``401`` on authentication failure, ``429`` rate limit.
        """
        return self._request("GET", ENDPOINT_ACCOUNT_PURCHASES).json()

    def get_credit_ledger(self) -> list:
        """Get the full credit ledger (all credit debits and credits) for this API key.

        Corresponds to ``GET /account/creditLedger``.

        :returns: List of ledger entries.

        :raises LynqaClientError: ``401`` on authentication failure, ``429`` rate limit.
        """
        return self._request("GET", ENDPOINT_ACCOUNT_CREDIT_LEDGER).json()
