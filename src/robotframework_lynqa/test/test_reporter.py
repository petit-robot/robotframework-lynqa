"""Unit tests for :class:`robotframework_lynqa.reporter.StepReporter`.

These tests exercise the reporter in isolation from Robot Framework: the Robot ``logger`` is patched to capture the
messages, and the Lynqa client is a mock, so only the reporter's own log-presentation logic is under test.
"""

import pytest

from robotframework_lynqa.reporter import StepReporter
from robotframework_lynqa.test.data_set.testrun_full_status import TEST_RUN_FULL_STATUS_SUCCESS_RESPONSE
from robotframework_lynqa.test.data_set.testrun_full_status_failure import TEST_RUN_FULL_STATUS_FAILURE_RESPONSE

# Screenshots embedded for the sample runs: 1 initial + 5 command + 5 assertion screenshots.
EXPECTED_SCREENSHOT_COUNT = 11


@pytest.fixture
def reporter(mocker, screenshot_base64):
    """Build a :class:`StepReporter` wired to the given client and run data."""
    client = mocker.patch("pylynqa.LynqaClient")
    client.get_screenshot.return_value = screenshot_base64
    return StepReporter(client, run_id="ur35vkfr7k5rm321dsuvllab", url="https://petit-robot.bzh")


@pytest.fixture
def mock_logger(mocker):
    """Fixture to intercept logger calls."""
    return mocker.patch("robotframework_lynqa.reporter.logger")


def _embedded_image_count(mock_logger):
    """Count the log messages that embedded an inline screenshot."""
    messages = [call.args[0] for call in mock_logger.info.call_args_list]
    messages += [call.args[0] for call in mock_logger.write.call_args_list]
    return sum("<img" in message for message in messages)


@pytest.mark.parametrize(
    "results",
    [TEST_RUN_FULL_STATUS_SUCCESS_RESPONSE, TEST_RUN_FULL_STATUS_FAILURE_RESPONSE],
    ids=["success", "failure"],
)
def test_log_step_embeds_every_screenshot(reporter, mock_logger, results):
    """Every screenshot (initial + commands + assertions) is fetched and embedded as an inline image."""
    # Act
    for index, _ in enumerate(results["stepStatuses"]):
        reporter.log_step(index, results)

    # Assert
    assert reporter._client.get_screenshot.call_count == EXPECTED_SCREENSHOT_COUNT
    assert _embedded_image_count(mock_logger) == EXPECTED_SCREENSHOT_COUNT


def test_embed_screenshot_catches_fetch_errors(reporter, mock_logger):
    """A screenshot download error is caught and logged, returning an empty string instead of raising."""
    # Arrange
    reporter._client.get_screenshot.side_effect = Exception("Kenavo")

    # Act / Assert
    assert not reporter._embed_screenshot("415bceb6-9328-4c50-80b3-d0139f8bcafe", "caption")
    mock_logger.error.assert_called_once()
