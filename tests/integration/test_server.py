# encoding=utf-8
import logging
import platform
from pathlib import Path

import pytest
import requests
from brunns.matchers.object import has_identical_properties_to
from brunns.matchers.response import is_response
from hamcrest import assert_that, contains_inanyorder

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
        response = requests.get(f"{imposter.url}/test")

        assert_that(
            response, is_response().with_status_code(200).and_body("sausages"),
        )
        assert_that(
            server, had_request().with_path("/test").and_method("GET"),
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

            response1 = requests.get(f"{imposter1.url}/test")
            response2 = requests.get(f"{imposter2.url}/test")

            assert_that(response1, is_response().with_status_code(200).and_body("sausages"))
            assert_that(response2, is_response().with_status_code(200).and_body("bacon"))

    finally:
        server1.close()
        server2.close()


def test_query_all_imposters(mock_server):
    imposter1 = Imposter(Stub(Predicate(path="/test1"), Response(body="sausages")))
    imposter2 = Imposter(Stub(Predicate(path="/test2"), Response(body="egg")))

    with mock_server([imposter1, imposter2]) as server:
        actual = list(server.query_all_imposters())
        assert_that(
            actual,
            contains_inanyorder(
                has_identical_properties_to(
                    imposter1,
                    ignoring={"host", "url", "server_url", "configuration_url", "attached"},
                ),
                has_identical_properties_to(
                    imposter2,
                    ignoring={"host", "url", "server_url", "configuration_url", "attached"},
                ),
            ),
        )
