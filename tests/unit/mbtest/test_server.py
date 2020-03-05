# encoding=utf-8
import logging
from unittest.mock import patch

from mbtest.server import ExecutingMountebankServer

logger = logging.getLogger(__name__)


def test_server_default_options():
    # Given
    with patch("subprocess.Popen") as popen, patch("requests.get"):

        # When
        ExecutingMountebankServer(port=1234)

        # Then
        popen.assert_called_with(
            [
                "node_modules/.bin/mb",
                "start",
                "--port",
                "1234",
                "--debug",
                "--allowInjection",
                "--localOnly",
                "--datadir",
                ".mbdb",
            ]
        )


def test_server_non_default_options():
    # Given
    with patch("subprocess.Popen") as popen, patch("requests.get"):

        # When
        ExecutingMountebankServer(
            executable="somepath/mb",
            port=3456,
            debug=False,
            allow_injection=False,
            local_only=False,
            data_dir=None,
        )

        # Then
        popen.assert_called_with(["somepath/mb", "start", "--port", "3456"])
