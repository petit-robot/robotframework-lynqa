"""Lynqa Robot Framework library implementation."""

from pylynqa import LynqaClient
from robot.api.interfaces import ListenerV3

BASE_URL = "https://api.lynqa.smartesting.com"


class LynqaLibrary(ListenerV3):
    """Robot Framework library for executing Lynqa test runs."""

    ROBOT_LIBRARY_SCOPE = "TEST"
    ROBOT_LISTENER_API_VERSION = 3

    def __init__(self, api_key: str, base_url: str = BASE_URL) -> None:
        """Initialize Lynqa Library."""
        self.ROBOT_LIBRARY_LISTENER = self
        self._client = LynqaClient(api_key=api_key, base_url=base_url)
