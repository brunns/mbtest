# encoding=utf-8
import logging
from unittest.mock import patch, MagicMock
from pathlib import Path

from mbtest.server import (
    DEFAULT_MB_EXECUTABLE,
    find_mountebank_install,
    ExecutingMountebankServer,
)

logger = logging.getLogger(__name__)


def test_find_mountebank_install(monkeypatch):
    linux_mb_name = "mb"
    windows_mb_name = "mb.cmd"
    user_home = "/home/user"
    user_bin = "node_modules/.bin"

    with patch("platform.system", return_value="Windows"):
        assert find_mountebank_install() == "%s/%s" % (user_bin, windows_mb_name)

    monkeypatch.setenv("HOME", user_home)
    with patch("platform.system", return_value="Linux"):
        with patch("pathlib.Path.is_file", return_value=True):
            assert find_mountebank_install() == "%s/%s/%s" % (
                user_home,
                user_bin,
                linux_mb_name,
            )


def test_server_default_options():
    # Given
    with patch("subprocess.Popen") as popen, patch("requests.get"):

        # When
        ExecutingMountebankServer(port=1234)

        # Then
        popen.assert_called_with(
            [
                DEFAULT_MB_EXECUTABLE,
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
