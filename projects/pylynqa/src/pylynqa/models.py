"""Data models for Lynqa API: test steps, test data, and test run context."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class TextualData:
    """A guidance hint passed to the Lynqa agent during test execution.

    :param text: Plain-text guidance, e.g. ``'The user is between 18 and 49'``.
    """

    text: str

    def to_dict(self) -> dict:
        """Transform to a JSON-compatible dict."""
        return {"text": self.text}


@dataclass
class CreateAttachment:
    """A file attachment to include with a test run (creation only).

    :param name: File name, e.g. ``'invoice_260313.pdf'``.
    :param data: Base64-encoded data URI, e.g. ``'data:text/plain;base64,SGVsbG8gd29ybGQh'``.
    """

    name: str
    data: str

    def to_dict(self) -> dict:
        """Transform to a JSON-compatible dict."""
        return {"name": self.name, "data": self.data}


@dataclass
class Attachment:
    """A file attachment returned by the API (server-assigned id).

    :param name: File name, e.g. ``'invoice_260313.pdf'``.
    :param id: UUID of the attachment assigned by the server.
    """

    name: str
    id: str


@dataclass
class CreateTestStep:
    """A single step to include when creating a test run.

    :param action: Human-readable description of the action to perform, e.g. ``'Click on the "Login" button'``.
    :param expected_result: Optional assertion that should hold after the action is executed, e.g. ``'The user is
        redirected to /dashboard'``.
    :param guidance: Optional guidance hints to help the agent execute this step.
    :param attachments: Optional file attachments for this step (base64-encoded).
    """

    action: str
    expected_result: str | None = None
    guidance: list[TextualData] = field(default_factory=list)
    attachments: list[CreateAttachment] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Serialise to a JSON-compatible dict.

        :returns: Dict with ``action`` and, when set, optional fields.
        """
        d: dict = {"action": self.action}
        if self.expected_result is not None:
            d["expectedResult"] = self.expected_result
        if self.guidance:
            d["guidance"] = [g.to_dict() for g in self.guidance]
        if self.attachments:
            d["attachments"] = [a.to_dict() for a in self.attachments]
        return d


@dataclass
class TestStep:
    """A single step returned by the API for a test run.

    :param action: Human-readable description of the action performed.
    :param expected_result: Assertion associated with this step, if any.
    :param guidance: Guidance hints attached to this step.
    :param attachments: File attachments returned by the server (read-only, server-assigned ids).
    """

    action: str
    expected_result: str | None = None
    guidance: list[TextualData] = field(default_factory=list)
    attachments: list[Attachment] = field(default_factory=list)


@dataclass
class TestData:
    """A name/value pair used to inject secrets or test data into test steps.

    :param name: Name of the data entry, e.g. ``'password'``.
    :param value: Value of the data entry, e.g. ``'mys3cr3t!'``.
    """

    name: str
    value: str

    def to_dict(self) -> dict:
        """Serialise to a JSON-compatible dict.

        :returns: Dict with ``name`` and ``value``.
        """
        return {"name": self.name, "value": self.value}


@dataclass
class TestRunContext:
    """Optional context attached to a test run.

    Provides locale information and secrets that the Lynqa engine can use when executing the test steps.

    :param client_language: BCP-47 language tag or plain language name representing the browser locale, e.g.
        ``'en-US'``.
    :param client_datetime: Human-readable local date/time string passed to the agent, e.g. ``'Thu Feb 26 2026 09:26:12
        GMT+0100'``.
        :param secrets: List of :class:`TestData` entries that will be injected into the test steps at execution time.
    """

    client_language: str | None = None
    client_datetime: str | None = None
    secrets: list[TestData] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Serialise to a JSON-compatible dict, omitting unset fields.

        :returns: Dict representation of the context.
        """
        d: dict = {}
        if self.client_language is not None:
            d["clientLanguage"] = self.client_language
        if self.client_datetime is not None:
            d["clientDatetime"] = self.client_datetime
        if self.secrets:
            d["secrets"] = [s.to_dict() for s in self.secrets]
        return d


@dataclass
class TimePeriod:
    """A relative time window used in :class:`TestRunsFilter`.

    :param count: Number of units, e.g. ``3`` for "last 3 hours".
    :param unit: Time unit — ``'m'`` minutes, ``'h'`` hours, ``'d'`` days, ``'M'`` months.
    """

    count: int
    unit: str

    def to_dict(self) -> dict:
        """Transform to a JSON-compatible dict."""
        return {"count": self.count, "unit": self.unit}


@dataclass
class TestRunsFilter:
    """Filter criteria for :meth:`~pylynqa.client.LynqaClient.query_test_runs`.

    All fields are optional; omitted fields are not sent in the request body.

    :param statuses: Keep only runs with these statuses. Allowed values: ``'waiting'``, ``'running'``,
        ``'success'``, ``'failed'``, ``'error'``, ``'stopped'``, ``'not_run'``.
    :param relative_period: Relative time window, e.g. ``TimePeriod(count=3, unit='h')`` for the last 3 hours.
    :param start_date: Start of an explicit date range (ISO 8601).
    :param end_date: End of an explicit date range (ISO 8601).
    :param api_key_ids: Keep only runs created by these API key IDs.
    :param test_run_ids: Keep only runs with these IDs.
    """

    statuses: list[str] | None = None
    relative_period: TimePeriod | None = None
    start_date: str | None = None
    end_date: str | None = None
    api_key_ids: list | None = None
    test_run_ids: list | None = None

    def to_dict(self) -> dict:
        """Transform to a JSON-compatible dict."""
        d: dict = {}
        if self.statuses is not None:
            d["statuses"] = self.statuses
        if self.relative_period is not None:
            d["relativePeriod"] = self.relative_period.to_dict()
        if self.start_date is not None:
            d["startDate"] = self.start_date
        if self.end_date is not None:
            d["endDate"] = self.end_date
        if self.api_key_ids is not None:
            d["apiKeyIds"] = self.api_key_ids
        if self.test_run_ids is not None:
            d["testRunIds"] = self.test_run_ids
        return d


class LynqaClientError(Exception):
    """Raised when the Lynqa API returns a non-2xx HTTP response.

    :param status_code: HTTP status code returned by the server.
    :param error: Short error label from the response body (e.g. ``'Unauthorized'``).
    :param message: Human-readable description from the response body (e.g. ``'Missing authentication method'``).

    Common status codes:

    - ``400`` - Request body is malformed.
    - ``401`` - Authentication failed (invalid or missing API key).
    - ``403`` - Not enough credits to execute the test.
    - ``404`` - Resource not found.
    - ``410`` - Test run has expired.
    - ``422`` - URL is not safe to test.
    - ``429`` - Too many requests (rate limit exceeded).
    """

    def __init__(self, status_code: int, error: str = "", message: str = "") -> None:
        """Initialize the LynqaClientError."""
        self.status_code = status_code
        self.error = error
        self.message = message
        super().__init__(f"HTTP {status_code}: {error}" + (f" - {message}" if message else ""))
