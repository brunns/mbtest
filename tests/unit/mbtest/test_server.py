# encoding=utf-8
import logging
from pathlib import Path
from unittest.mock import patch

from brunns.matchers.mock import call_has_args as with_args
from brunns.matchers.mock import has_call
from hamcrest import assert_that, contains_exactly, contains_string

from mbtest.server import ExecutingMountebankServer

logger = logging.getLogger(__name__)


def test_server_default_options():
    # Given
    with patch("subprocess.Popen") as popen, patch("requests.get"):
        # When
        ExecutingMountebankServer(port=1234)

        # Then
        assert_that(
            popen,
            has_call(
                with_args(
                    contains_exactly(
                        contains_string("mb"),
                        "start",
                        "--port",
                        "1234",
                        "--debug",
                        "--allowInjection",
                        "--localOnly",
                        "--datadir",
                        ".mbdb",
                    )
                )
            ),
        )


def test_server_non_default_options():
    # Given
    with patch("subprocess.Popen") as popen, patch("requests.get"):
        # When
        ExecutingMountebankServer(
            executable=Path("somepath/mb"),
            port=3456,
            debug=False,
            allow_injection=False,
            local_only=False,
            data_dir=None,
        )

        # Then
        assert_that(
            popen,
            has_call(with_args(contains_exactly(contains_string("mb"), "start", "--port", "3456"))),
        )
