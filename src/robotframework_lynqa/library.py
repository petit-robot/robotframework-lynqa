"""Robot Framework test library and listener for the Lynqa execution agent.

This module exposes :class:`LynqaLibrary`, a Robot Framework library that lets
you write scenarios in plain Gherkin and have them executed by the Lynqa AI
agent instead of by locally defined keywords.

Scenarios are written with the ``Given``/``When``/``Then``
keywords, each taking a single natural-language step as its argument::

    *** Settings ***
    Library    robotframework_lynqa.LynqaLibrary    api_key=%{API_KEY}

    *** Variables ***
    ${LYNQA_URL}    https://example.com/

    *** Tasks ***
    Search For An Item
        Given    the home page is open
        When     the user searches for an item
        Then     matching results are displayed
"""

import logging
import time
from datetime import datetime
from typing import Any

import pylynqa
from pylynqa import LynqaClient, TestData, TestRunContext
from robot.api import SuiteVisitor, logger
from robot.api.interfaces import ListenerV3
from robot.libraries.BuiltIn import BuiltIn

BASE_URL = "https://api.lynqa.smartesting.com"

GHERKIN_KEYWORDS = ("Given", "When", "Then", "And", "But")

# Statuses that mean the run is not finished yet.
PENDING_STATUSES = ("waiting", "running", "not_run")

# How often to poll the run status, and how long to wait before giving up.
POLL_INTERVAL_SECONDS = 5
RUN_TIMEOUT_SECONDS = 300

# Variable names
URL_VAR = "${LYNQA_URL}"
LANGUAGE_VAR = "${LYNQA_LANGUAGE}"
DATETIME_VAR = "${LYNQA_DATETIME}"
SECRETS_VAR = "&{LYNQA_SECRETS}"


class _GherkinStepCollector(SuiteVisitor):
    """Collect the Gherkin steps of a running test case.

    Walks a Robot Framework test case and records every keyword call whose name
    is one of :data:`GHERKIN_KEYWORDS`, rebuilding the original Gherkin step
    (keyword name followed by its argument text).
    """

    def __init__(self) -> None:
        """Initialize the collector with an empty list of steps."""
        self.steps: list[str] = []

    def start_keyword(self, keyword) -> None:
        """Record the keyword when it is one of the Gherkin step keywords.

        :param keyword: Running keyword visited by Robot Framework.
        """
        if keyword.name in GHERKIN_KEYWORDS:
            text_step = ""
            if len(keyword.args) > 0:
                text_step = keyword.args[0]
            self.steps.append(f"{keyword.name} {text_step}")


class LynqaLibrary(ListenerV3):
    """Robot Framework library that runs Gherkin scenarios via Lynqa.

    Acts both as a test library exposing the Gherkin step keywords
    (``Given``/``When``/``Then``/``And``/``But``) and as a listener
    (``ROBOT_LIBRARY_LISTENER``) that captures each scenario on
    :meth:`start_test` and submits it to the Lynqa execution agent.

    See the :mod:`~robotframework_lynqa.library` module documentation for the
    configuration variables and a usage example.
    """

    ROBOT_LIBRARY_SCOPE = "TEST"

    def __init__(self, api_key: str, base_url: str = BASE_URL) -> None:
        """Initialize the Lynqa library.

        :param api_key: API key used to authenticate against the Lynqa service.
        :param base_url: Base URL of the Lynqa API. Defaults to :data:`BASE_URL`.
        """
        self.ROBOT_LIBRARY_LISTENER = self
        self._init_client(api_key, base_url)
        self._run_id: str = ""
        self._start_error: Exception | None = None
        self._step_index: int = 0

        self.scenario: str = ""
        self.url: str | None = ""
        self.context: TestRunContext = TestRunContext()
        self.results: dict[str, Any] = {}

    def _init_client(self, api_key: str, base_url: str):
        """Initialize the Lynqa client with the good parameters.

        :param api_key: API key used to authenticate against the Lynqa service.
        :param base_url: Base URL of the Lynqa API.
        """
        pylynqa.client._PACKAGE_CONSUMER_NAME = "petit-robot:robotframework-lynqa"  # ty: ignore[invalid-assignment]   # ruff: ignore[private-member-access]
        self._client = LynqaClient(api_key=api_key, base_url=base_url)

    # ------------------------------------------------------------------
    # Listener interface
    # ------------------------------------------------------------------

    def start_test(self, data, result) -> None:
        """Collect the scenario's Gherkin steps when a test starts.

        Reads the running test case with a :class:`_GherkinStepCollector` visitor and
        stores its ``Given``/``When``/``Then``/``And``/``But`` steps as the
        current scenario.

        Any exception raised while preparing the run is captured and turned into
        a test failure in :meth:`end_test` (a status set here would otherwise be
        overwritten when the test body runs).

        :param data: Running test case provided by Robot Framework.
        :param result: Test result object provided by Robot Framework.
        """

        def collect_steps(data):
            """Collect the Gherkin steps from the running test case."""
            collector = _GherkinStepCollector()
            data.visit(collector)
            return collector.steps

        self._start_error = None
        self._step_index = 0
        try:
            self.scenario = "\n".join(collect_steps(data))
            url = self._search_variable(URL_VAR)
            self.url = None if url is None else str(url)
            self.context = self._search_context()
            self._execute_lynqa_testrun(name=data.name)
        except Exception as error:
            logging.exception("Lynqa run preparation failed")
            self._start_error = error

    def end_test(self, data, result) -> None:
        """Fail the current test if :meth:`start_test` caught an exception.

        :param data: Running test case provided by Robot Framework.
        :param result: Test result object provided by Robot Framework.
        """
        if self._start_error is not None:
            result.status = "FAIL"
            result.message = f"Lynqa execution failed: {self._start_error}"
            return

        self._report_test_results(result)

    def start_keyword(self, data, result) -> None:
        """Log the commands and assertions of a Gherkin keyword's Lynqa step.

        Logging happens here, when the keyword starts, rather than in the keyword
        body: Robot Framework stops executing the bodies of the keywords that
        follow a failed one, but ``start_keyword`` still fires for them, so every
        Gherkin keyword gets its logs. The step is matched in execution order via
        :attr:`_step_index`, which is only incremented later in :meth:`end_keyword`.

        :param data: Running keyword provided by Robot Framework.
        :param result: Keyword result object provided by Robot Framework.
        """
        if data.name not in GHERKIN_KEYWORDS:
            return
        self._log_step_details()

    def end_keyword(self, data, result) -> None:
        """Set each Gherkin keyword's status from its matching Lynqa step.

        Only the Gherkin step keywords are reported; other keywords (logging,
        setup, ...) keep the status Robot Framework gave them.

        :param data: Running keyword provided by Robot Framework.
        :param result: Keyword result object provided by Robot Framework.
        """
        if data.name not in GHERKIN_KEYWORDS:
            return
        steps = self.results.get("stepStatuses", [])
        if self._step_index < len(steps):
            step_status = steps[self._step_index].get("status")
        else:
            # No per-step detail: fall back to the overall run status.
            step_status = self.results.get("status")
        result.status = "PASS" if step_status == "success" else "FAIL"
        self._step_index += 1

    def _execute_lynqa_testrun(self, name: str, timeout: float = RUN_TIMEOUT_SECONDS):
        """Start a Lynqa test run and wait for it to reach a final status.

        Polls the run status every :data:`POLL_INTERVAL_SECONDS` seconds until it
        leaves the :data:`PENDING_STATUSES`, giving up after ``timeout`` seconds so
        the run cannot hang forever when a final status is never reached.

        :param name: Name of the test run.
        :param timeout: Maximum time, in seconds, to wait for the run to finish.
        :raises TimeoutError: If the run is still pending once ``timeout`` elapses.
        """
        if not self.url:
            raise ValueError(f"No URL configured. Please set the {URL_VAR} variable.")  # ruff: ignore[raise-vanilla-args]

        self._run_id = self._client.add_gherkin_test_run(
            url=self.url,
            name=name,
            scenario=self.scenario,
        )
        logging.info(f"Testrun ID is: {self._run_id}")
        self._wait_until_testrun_end(timeout)
        self.results = self._client.get_test_run_full_status(self._run_id)

    def _wait_until_testrun_end(self, timeout: float):
        """Wait until the test run reaches a final status."""
        deadline = time.monotonic() + timeout
        while True:
            status = self._client.get_test_run_status(self._run_id).get("status")
            logging.debug(f"Current run status: {status}")
            if status not in PENDING_STATUSES:
                return
            if time.monotonic() >= deadline:
                msg = f"Lynqa test run {self._run_id} did not complete within {timeout}s"
                raise TimeoutError(msg)
            time.sleep(POLL_INTERVAL_SECONDS)

    def _report_test_results(self, result):
        """Report the test results from the Lynqa API."""
        if self.results.get("status") == "success":
            result.status = "PASS"
        else:
            result.status = "FAIL"

        result.message = self.results.get("statusMessage")

    # ------------------------------------------------------------------
    # Keywords exposed to Robot Framework
    # ------------------------------------------------------------------

    def given(self, text: str) -> None:
        """Add a ``Given`` step to the current scenario.

        :param text: Natural-language description of the step.
        """

    def when(self, text: str) -> None:
        """Add a ``When`` step to the current scenario.

        :param text: Natural-language description of the step.
        """

    def then(self, text: str) -> None:
        """Add a ``Then`` step to the current scenario.

        :param text: Natural-language description of the step.
        """

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _log_step_details(self) -> None:
        """Log the commands and assertions of the current Gherkin step.

        Adds two log messages to the running keyword: a ``Commands:`` list with one
        ``- name: value`` bullet per command and an ``Assertions:`` list with one
        ``- assertion`` bullet per assertion. The step is the one matching the
        keyword at :attr:`_step_index`.
        """
        steps = self.results.get("stepStatuses", [])
        if self._step_index >= len(steps):
            return
        step = steps[self._step_index]

        commands = step.get("commands") or []
        command_lines = [
            f"- {command.get('name')}: {command['value']}" if "value" in command else f"- {command.get('name')}"
            for command in commands
        ]
        logger.info("\n".join(["Commands:", *command_lines]))

        report = step.get("assertionsReport") or {}
        assertions = report.get("assertions") or []
        assertion_lines = [f"- {item['assertion']}" for item in assertions if "assertion" in item]
        logger.info("\n".join(["Assertions:", *assertion_lines]))

    @staticmethod
    def _search_variable(variable_name) -> object:
        return BuiltIn().get_variable_value(variable_name)

    def _search_secrets_variables(self) -> list[TestData]:
        """Convert the secrets variable into a list of :class:`TestData`.

        The ``&{LYNQA_SECRETS}`` variable is expected to be a mapping of secret
        name to value, e.g. ``login=superu    password=TrèsS3cr3t``. Each entry
        is turned into a :class:`TestData` name/value pair.

        :returns: The secrets as :class:`TestData` items, or an empty list if unset.
        :raises TypeError: If the secrets variable is not a name/value mapping.
        """
        raw_secrets = self._search_variable(SECRETS_VAR)
        if not raw_secrets:
            return []
        if not isinstance(raw_secrets, dict):
            raise TypeError("Invalid secrets variable, expected a dict")  # ruff: ignore[raise-vanilla-args]
        return [TestData(name=str(name), value=str(value)) for name, value in raw_secrets.items()]

    def _search_context(self) -> TestRunContext:
        client_language = self._search_variable(LANGUAGE_VAR)
        client_datetime = self._search_variable(DATETIME_VAR)
        if client_datetime is None:
            client_datetime = datetime.now().astimezone().strftime("%a %b %d %Y %H:%M:%S GMT%z")
        secrets = self._search_secrets_variables()
        return TestRunContext(
            client_language=str(client_language), client_datetime=str(client_datetime), secrets=secrets
        )
