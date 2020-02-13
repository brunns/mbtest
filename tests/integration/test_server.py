# encoding=utf-8
import logging
import platform
from pathlib import Path

import pytest
import requests
from brunns.matchers.response import response_with
from hamcrest import assert_that, is_
from mbtest.imposters import Imposter, Predicate, Response, Stub
from mbtest.matchers import had_request
from mbtest.server import (
    ExecutingMountebankServer,
    MountebankPortInUseException,
    MountebankTimeoutError,
)

logger = logging.getLogger(__name__)


def test_request_to_mock_server(mock_server):
    # Start mock server with required behavior
    imposter = Imposter(Stub(Predicate(path="/test"), Response(body="sausages")))

    with mock_server(imposter) as server:
        # Make request to mock server
        response = requests.get("{0}/test".format(imposter.url))

        assert_that(
            "We got the expected response",
            response,
            is_(response_with(status_code=200, body="sausages")),
        )
        assert_that(
            "The mock server recorded the request", server, had_request(path="/test", method="GET")
        )


def test_nonexistent_executable():
    with pytest.raises(OSError):
        ExecutingMountebankServer(executable=str(Path(".") / "no" / "such" / "path"), port=2526)


def test_non_executable():
    with pytest.raises(OSError):
        ExecutingMountebankServer(executable=str(Path(".") / "README.md"), port=2526)


def test_executable_not_mb():
    with pytest.raises(MountebankTimeoutError):
        ExecutingMountebankServer(executable="ls", port=2526, timeout=1)


def test_exception_running_multiple_servers_on_same_port():
    # Given
    with pytest.raises(MountebankPortInUseException):
        try:
            server1 = ExecutingMountebankServer(port=2526)
            server2 = ExecutingMountebankServer(port=2526)
        finally:
            try:
                server1.close()
                server2.close()
            except UnboundLocalError:
                pass


def test_server_can_be_restarted_on_same_port():
    server = ExecutingMountebankServer(port=2526)
    server.close()

    server = ExecutingMountebankServer(port=2526)
    server.close()


@pytest.mark.skipif(
    platform.system() == "Windows", reason="Can only run one server on Windows for some reason."
)
def test_allow_multiple_servers_on_different_ports():
    # Given
    try:
        server1 = ExecutingMountebankServer(port=2526)
        server2 = ExecutingMountebankServer(port=2527)
        imposter1 = Imposter(Stub(Predicate(path="/test"), Response(body="sausages")))
        imposter2 = Imposter(Stub(Predicate(path="/test"), Response(body="bacon")))

        with server1(imposter1), server2(imposter2):

            response1 = requests.get("{0}/test".format(imposter1.url))
            response2 = requests.get("{0}/test".format(imposter2.url))

            assert_that(response1, is_(response_with(status_code=200, body="sausages")))
            assert_that(response2, is_(response_with(status_code=200, body="bacon")))

    finally:
        server1.close()
        server2.close()
