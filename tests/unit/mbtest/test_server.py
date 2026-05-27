import logging
from http import HTTPStatus
from pathlib import Path
from unittest.mock import patch

from brunns.matchers.mock import call_has_args as with_args
from brunns.matchers.mock import has_call
from brunns.matchers.url import is_url
from hamcrest import assert_that, contains_exactly, contains_string, has_entries, has_length
from respx import Router

from mbtest.imposters import Imposter, Response, Stub
from mbtest.server import ExecutingMountebankServer, MountebankServer

logger = logging.getLogger(__name__)


def test_server_default_options(httpx2_mock: Router):
    # Given
    httpx2_mock.get().respond(status_code=HTTPStatus.OK)
    with patch("subprocess.Popen") as popen:
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


def test_get_replayable_imposter(httpx2_mock: Router):
    # Given
    server = MountebankServer(port=2525)
    imposter = Imposter(Stub(responses=Response(body="hello")), port=4567)
    imposter.attach("localhost", 4567, server.server_url)

    httpx2_mock.get().respond(
        status_code=HTTPStatus.OK,
        json={
            "protocol": "http",
            "port": 4567,
            "stubs": [{"responses": [{"is": {"statusCode": 200, "body": "hello"}}], "predicates": []}],
        },
    )

    # When
    result = server.get_replayable_imposter(imposter)

    # Then
    assert result.port == 4567
    assert_that(result.stubs, has_length(1))

    call = httpx2_mock.calls.last
    assert_that(call.request.url, is_url().with_query(has_entries(replayable="true", removeProxies="true")))


def test_server_non_default_options(httpx2_mock: Router):
    # Given
    httpx2_mock.get().respond(status_code=HTTPStatus.OK)
    with patch("subprocess.Popen") as popen:
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
