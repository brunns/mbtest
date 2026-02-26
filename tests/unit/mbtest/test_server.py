import logging
from pathlib import Path
from unittest.mock import MagicMock, patch

from brunns.matchers.mock import call_has_args as with_args
from brunns.matchers.mock import has_call
from hamcrest import assert_that, contains_exactly, contains_string

from mbtest.imposters import Imposter, Response, Stub
from mbtest.server import ExecutingMountebankServer, MountebankServer

logger = logging.getLogger(__name__)


def test_server_default_options():
    # Given
    with patch("subprocess.Popen") as popen, patch("httpx.get"):
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


def test_get_replayable_imposter():
    # Given
    server = MountebankServer(port=2525)
    imposter = Imposter(Stub(responses=Response(body="hello")), port=4567)
    imposter.attach("localhost", 4567, server.server_url)

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "protocol": "http",
        "port": 4567,
        "stubs": [{"responses": [{"is": {"statusCode": 200, "body": "hello"}}], "predicates": []}],
    }

    with patch("httpx.get", return_value=mock_response) as mock_get:
        # When
        result = server.get_replayable_imposter(imposter)

    # Then
    assert result.port == 4567
    assert len(result.stubs) == 1
    called_url = str(mock_get.call_args[0][0])
    assert "replayable=true" in called_url
    assert "removeProxies=true" in called_url


def test_server_non_default_options():
    # Given
    with patch("subprocess.Popen") as popen, patch("httpx.get"):
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
