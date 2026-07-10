"""Robot Framework log presentation for Lynqa test runs."""

from __future__ import annotations

from typing import TYPE_CHECKING

from robot.api import logger

if TYPE_CHECKING:
    from pylynqa import LynqaClient


class StepReporter:
    """Render the Robot log for one Lynqa test run step.

    Holds the run data needed to embed screenshots and caption commands and assertions, and exposes :meth:`log_step` to
    log a single step's details under the current keyword.
    """

    def __init__(self, client: LynqaClient, run_id: str, url: str | None) -> None:
        """Initialize the reporter for a single run.

        :param client: Lynqa client used to fetch screenshots.
        :param run_id: Identifier of the Lynqa test run.
        :param url: URL the run was started against, shown with the initial screenshot.
        """
        self._client = client
        self._run_id = run_id
        self._url = url

    def log_step(self, step_index: int, results: dict) -> None:
        """Log the commands and assertions of a Gherkin step.

        Logs a ``Command`` list with one log per command and an ``Assertion`` list with one log per assertion, each
        followed by its screenshots if any. The initial screenshot captured before the run is embedded once, ahead of
        the first step's commands. The step is the one at ``step_index`` in the run's ``stepStatuses``.

        :param step_index: Index of the step to log, in execution order.
        :param results: Full status of the run, as returned by the Lynqa API.
        """
        steps = results.get("stepStatuses", [])
        if step_index >= len(steps):
            return
        step = steps[step_index]

        if step_index == 0:
            self._log_initial_report(results)
        self._log_step_commands(step)
        self._log_step_assertions(step)

    def _log_initial_report(self, results) -> None:
        """Log the initial report (global info).

        :param results: Full status of the run, as returned by the Lynqa API.
        """
        initial_report = results.get("initialReport", {})
        logger.info(self._embed_screenshot(initial_report.get("screenshot"), f"Open URL {self._url}"), html=True)

    def _log_step_commands(self, step: dict) -> None:
        """Log the current step's commands and embed their screenshots.

        :param step: The step from the run's ``stepStatuses`` to log.
        """

        def _is_response_success(command):
            return "success" in command.get("response", {})

        for command in step.get("commands", []):
            level = "INFO" if _is_response_success(command) else "ERROR"
            logger.write(
                self._embed_screenshot(command.get("screenshot"), self._command_caption(command)),
                level=level,
                html=True,
            )

    @staticmethod
    def _command_caption(command: dict) -> str:
        """Build a human-readable caption for a command's screenshot.

        :param command: A command entry from a step's ``commands`` list.

        :returns: The command name enriched with available information.
        """
        caption = f"Command: {command.get('name', '')}"
        if "value" in command:
            caption += f"(value: {command['value']})"
        elif "button" in command:
            caption += f"(button: {command['button']})"
        if command.get("htmlElement"):
            caption += f' on element "{command["htmlElement"]}"'
        return str(caption)

    def _log_step_assertions(self, step: dict) -> None:
        """Log the current step's assertions and embed the assertions report screenshot.

        :param step: The step from the run's ``stepStatuses`` to log.
        """

        def _is_assertion_checked(assertion):
            return assertion.get("checked", False)

        report = step.get("assertionsReport", {})
        assertions = report.get("assertions", [])

        for assertion in assertions:
            level = "INFO" if _is_assertion_checked(assertion) else "ERROR"
            logger.write(
                self._assertion_caption(assertion),
                level=level,
                html=True,
            )
        if "testVerdictCause" in step:
            logger.error(f"Verdict: {step['testVerdictCause']}")

        logger.info(self._embed_screenshot(report.get("screenshot"), ""), html=True)

    @staticmethod
    def _assertion_caption(assertion):
        """Build a human-readable caption for an assertion.

        :param assertion: An assertion entry from a step's ``assertionsReport`` assertions list.

        :returns: The assertion text enriched with available information.
        """
        caption = f'Assertion: "{assertion.get("assertion", "")}"'
        return str(caption)

    def _embed_screenshot(self, screenshot_id: str | None, caption: str) -> str:
        """Fetch a Lynqa screenshot and return it embedded inline in an HTML string.

        Downloads the screenshot as base64-encoded PNG data and wraps it in an ``<img>`` inside a collapsible
        ``<details>`` block. A download failure is logged and caught, so it never fails the test run.

        :param screenshot_id: UUID of the screenshot to fetch, or ``None`` when the step has none.
        :param caption: Text shown above the embedded image.

        :returns: The caption and embedded image as an HTML string, or an empty string when there is no screenshot or
            the download failed.
        """
        if not screenshot_id:
            return ""
        try:
            data = self._client.get_screenshot(self._run_id, screenshot_id)
        except Exception as error:
            logger.error(f"Failed to fetch Lynqa screenshot {screenshot_id}: {error}")
            return ""
        return (
            f'{caption}<details><summary>screenshot</summary><img src="data:image/png;base64,{data}"'
            + 'style="max-width: 100%;"/></details>'
        )
