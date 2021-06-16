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

        assert_that(response, is_response().with_status_code(200).and_body("sausages"))
        assert_that(server, had_request().with_path("/test").and_method("GET"))


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
        actual = server.query_all_imposters()
        assert_that(
            actual,
            contains_inanyorder(
                has_identical_properties_to(imposter1), has_identical_properties_to(imposter2)
            ),
        )


def test_removing_impostor_from_running_server(mock_server):
    # Set up server
    with mock_server(
        [
            Imposter(Stub(Predicate(path="/test"), Response(body="sausage")), name="sausage"),
            Imposter(Stub(Predicate(path="/test"), Response(body="egg")), name="egg"),
            Imposter(Stub(Predicate(path="/test"), Response(body="chips")), name="chips"),
        ]
    ) as server:

        # Retrieve impostor details from running server, and check they work
        initial = server.query_all_imposters()

        responses = [requests.get(f"{initial[i].url}/test") for i in range(3)]
        assert_that(
            responses,
            contains_inanyorder(
                is_response().with_body("sausage"),
                is_response().with_body("egg"),
                is_response().with_body("chips"),
            ),
        )

        # Delete one impostor, make sure it's gone, and that the rest still work
        egg_impostor = [i for i in initial if i.name == "egg"][0]
        other_impostors = [i for i in initial if i.name != "egg"]
        server.delete_impostor(egg_impostor)

        with pytest.raises(requests.exceptions.ConnectionError):
            requests.get(f"{egg_impostor.url}/test")
        responses = [requests.get(f"{i.url}/test") for i in other_impostors]
        assert_that(
            responses,
            contains_inanyorder(
                is_response().with_body("sausage"),
                is_response().with_body("chips"),
            ),
        )

        # Reset the server from the initial impostors, and check it's back to normal
        server.delete_imposters()
        server.add_imposters(initial)

        responses = [requests.get(f"{initial[i].url}/test") for i in range(3)]
        assert_that(
            responses,
            contains_inanyorder(
                is_response().with_body("sausage"),
                is_response().with_body("egg"),
                is_response().with_body("chips"),
            ),
        )
