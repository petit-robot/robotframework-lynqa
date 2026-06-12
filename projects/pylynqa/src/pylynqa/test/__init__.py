"""Unit tests for pylynqa."""

# ruff: file-ignore[non-empty-init-module]

import json
from collections.abc import Callable

import pytest

from pylynqa import BASE_URL
from pylynqa.models import LynqaClientError

API_KEY = "fake_api_key"

RESPONSE_ERROR = {"message": "", "error": "", "statusCode": 0}


def url(path: str) -> str:
    """Build a full API URL from a path."""
    return f"{BASE_URL}{path}"


def body(responses, call_num: int) -> dict:
    """Boilerplate function to return the body of the response."""
    return json.loads(responses.calls[call_num].request.body)


def create_http_response_error(status_code: int, error: str) -> dict:
    """Util function to create an http response error."""
    resp_error = RESPONSE_ERROR.copy()
    resp_error["error"] = error
    resp_error["statusCode"] = status_code
    return resp_error


def assert_raises_on_error(  # ruff: ignore[too-many-arguments,too-many-positional-arguments]
    responses,
    http_method: str,
    mock_url: str,
    client_call: Callable,
    status_code: int,
    error: str,
) -> None:
    """Assert that a client call raises LynqaClientError with the expected status code and error."""
    resp_error = create_http_response_error(status_code, error)
    responses.add(getattr(responses, http_method), mock_url, json=resp_error, status=status_code)
    with pytest.raises(LynqaClientError) as exc_info:
        client_call()
    assert exc_info.value.status_code == status_code
    assert exc_info.value.error == error
