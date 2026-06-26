"""Unit tests for robotframework_lynqa."""

from robot.api.interfaces import ListenerV3

# ruff: file-ignore[non-empty-init-module]
from robot.libraries.BuiltIn import BuiltIn

API_KEY = "fake_api_key"


class _CaptureLibInstance(ListenerV3):
    """Listener that captures the live LynqaLibrary instance during the run.

    The ``.robot`` file owns the :class:`LynqaLibrary` instance (it is created by the ``Library`` import), so the test
    cannot reference it directly. This listener grabs that instance from the running context before the test ends.
    """

    def __init__(self) -> None:
        """Initialize the capture listener."""
        self.instance = None

    def end_test(self, data, result) -> None:
        """Capture the library instance while the execution context is alive.

        :param data: Running test data passed by Robot Framework.
        :param result: Test result object passed by Robot Framework.
        """
        self.instance = BuiltIn().get_library_instance("robotframework_lynqa.LynqaLibrary")
