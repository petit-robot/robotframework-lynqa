"""Unit tests for robotframework_lynqa."""

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
import robot
from pylynqa import TestData, TestRunContext
from robot.result import ExecutionResult, Keyword

from robotframework_lynqa.library import LynqaLibrary
from robotframework_lynqa.test import API_KEY, _CaptureLibInstance
from robotframework_lynqa.test.data_set.testrun_full_status import TEST_RUN_FULL_STATUS_SUCCESS_RESPONSE
from robotframework_lynqa.test.data_set.testrun_full_status_failure import TEST_RUN_FULL_STATUS_FAILURE_RESPONSE

DATA_SET_FOLDER = Path(__file__).parent / "data_set"
TEST_LYNQA_ROBOT_FILE = DATA_SET_FOLDER / "test_lynqa_nominal.robot"
TEST_LYNQA_WITH_DATE_ROBOT_FILE = DATA_SET_FOLDER / "test_lynqa_with_date.robot"
TEST_LYNQA_WITHOUT_URL_ROBOT_FILE = DATA_SET_FOLDER / "test_lynqa_without_url.robot"
TEST_LYNQA_WITH_RESULTS_ROBOT_FILE = DATA_SET_FOLDER / "test_lynqa_with_results.robot"

EXPECTED_SCENARIO = (
    "Given the storefront is open at the home page\n"
    "When the user searches for an autonomous testing agent\n"
    "When the user filters the results to top-rated agents under 50 credits\n"
    "Then a list of matching AI agents is displayed with their prices\n"
    'Then the premium "Bobcat" agent is sold out because its success'
)


@pytest.fixture
def client(mocker):
    """Mock the Lynqa HTTP client so no real request is sent.

    Patches :class:`LynqaClient` in the library module: every ``LynqaLibrary``
    created during the run gets this mock as its ``_client``. The run is reported
    as an immediately successful one.

    :returns: The mock client instance shared by every ``LynqaLibrary``.
    """
    client = mocker.patch("robotframework_lynqa.library.LynqaClient").return_value
    client.add_gherkin_test_run.return_value = 123456
    client.get_test_run_status.return_value = {"status": "success"}
    client.get_test_run_full_status.return_value = {"status": "success", "statusMessage": "OK"}
    return client


@pytest.fixture
def listener_probe(monkeypatch, mocker, client):
    """Initialize the listener probe used to capture the library instance."""
    monkeypatch.setenv("API_KEY", API_KEY)
    mock_datetime = mocker.patch("robotframework_lynqa.library.datetime")
    fixed_now = datetime(2026, 6, 24, 9, 52, 0, tzinfo=timezone(timedelta(hours=2)))
    mock_datetime.now.return_value.astimezone.return_value = fixed_now
    return _CaptureLibInstance()


@pytest.fixture
def library(client):
    """Build a ``LynqaLibrary`` instance wired to the mocked client for unit tests.

    :returns: A library whose ``_client`` is the shared mock from ``client``.
    """
    return LynqaLibrary(api_key=API_KEY)


def test_nominal_scenario(tmp_path, listener_probe):
    """Test that the scenario is executed."""
    # Act
    rc = robot.run(str(TEST_LYNQA_ROBOT_FILE), outputdir=str(tmp_path), listener=listener_probe)

    # Assert
    listener_inst = listener_probe.instance
    assert rc == 0
    assert listener_inst is not None
    assert listener_inst.scenario == EXPECTED_SCENARIO
    assert listener_inst.url == "https://www.super-u.ai"
    assert listener_inst.context == TestRunContext(
        client_language="rf-RF",
        client_datetime="Wed Jun 24 2026 09:52:00 GMT+0200",
        secrets=[TestData(name="login", value="superu"), TestData(name="password", value="TrèsS3cr3t")],
    )


def test_variable_with_date(tmp_path, listener_probe):
    """Test that the scenario is executed with a provided date."""
    # Act
    rc = robot.run(str(TEST_LYNQA_WITH_DATE_ROBOT_FILE), outputdir=str(tmp_path), listener=listener_probe)

    # Assert
    listener_inst = listener_probe.instance
    assert rc == 0
    assert listener_inst.context == TestRunContext(
        client_language="rf-RF",
        client_datetime="Wed May 8 2026 09:00:00 GMT+0200",
        secrets=[TestData(name="login", value="superu"), TestData(name="password", value="TrèsS3cr3t")],
    )


def test_variable_without_url(tmp_path, listener_probe):
    """Test that the execution fails if URL is missing."""
    # Act
    rc = robot.run(str(TEST_LYNQA_WITHOUT_URL_ROBOT_FILE), outputdir=str(tmp_path), listener=listener_probe)

    # Assert
    assert rc > 0


def test_scenario_result(tmp_path, listener_probe, client):
    """Test that the scenario result is returned."""
    # Arrange
    client.get_test_run_full_status.return_value = TEST_RUN_FULL_STATUS_SUCCESS_RESPONSE
    # Act
    rc = robot.run(str(TEST_LYNQA_WITH_RESULTS_ROBOT_FILE), outputdir=str(tmp_path), listener=listener_probe)

    # Assert
    assert rc == 0
    robot_result = ExecutionResult(str(tmp_path / "output.xml"))
    # Assert Test status
    test = robot_result.suite.tests[0]
    assert test.status == "PASS"
    assert test.message == "OK"
    # Assert Keywords status
    keywords = [elt for elt in test.body if isinstance(elt, Keyword)]
    for keyword in keywords:
        assert keyword.status == "PASS"
    assert len(keywords[0].messages) > 1


def test_scenario_result_failure(tmp_path, listener_probe, client):
    """Test that the scenario result is failed."""
    # Arrange
    client.get_test_run_full_status.return_value = TEST_RUN_FULL_STATUS_FAILURE_RESPONSE

    # Act
    rc = robot.run(str(TEST_LYNQA_WITH_RESULTS_ROBOT_FILE), outputdir=str(tmp_path), listener=listener_probe)

    # Assert
    assert rc > 0
    robot_result = ExecutionResult(str(tmp_path / "output.xml"))
    # Assert Test status
    test = robot_result.suite.tests[0]
    assert test.status == "FAIL"
    assert test.message == "KO"
    # Assert Keywords status
    keywords = [elt for elt in test.body if isinstance(elt, Keyword)]
    keywords_status = [keyword.status for keyword in keywords]
    assert keywords_status == ["PASS", "PASS", "FAIL", "PASS", "FAIL"]
    assert len(keywords[0].messages) > 1


def test_wait_until_testrun_end_polls_until_complete(library, client, mocker):
    """Polling continues while the run is pending, then stops on a final status."""
    # Arrange
    mocker.patch("robotframework_lynqa.library.time.sleep")
    statuses = [
        {"status": "running"},
        {"status": "running"},
        {"status": "success"},
    ]
    client.get_test_run_status.side_effect = statuses

    # Act
    library._wait_until_testrun_end(timeout=100)

    # Assert
    assert client.get_test_run_status.call_count == len(statuses)


def test_wait_until_testrun_end_raises_on_timeout(library, client, mocker):
    """A run that never leaves a pending status raises ``TimeoutError``."""
    # Arrange
    mocker.patch("robotframework_lynqa.library.time.sleep")
    client.get_test_run_status.return_value = {"status": "running"}

    # Act / Assert
    with pytest.raises(TimeoutError):
        library._wait_until_testrun_end(timeout=-1)


def test_search_secrets_variables_unset(library, mocker):
    """An unset secrets variable yields an empty list."""
    # Arrange
    mocker.patch.object(library, "_search_variable", return_value=None)

    # Act / Assert
    assert library._search_secrets_variables() == []


def test_search_secrets_variables_invalid_type(library, mocker):
    """A non-mapping secrets variable raises ``TypeError``."""
    # Arrange
    mocker.patch.object(library, "_search_variable", return_value="not-a-dict")

    # Act / Assert
    with pytest.raises(TypeError):
        library._search_secrets_variables()
