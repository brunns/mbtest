import logging

import requests
from brunns.matchers.response import is_response
from hamcrest import assert_that

from mbtest.imposters import Stub, Predicate, Response, Imposter

logger = logging.getLogger(__name__)


def test_not_existing_imposter_single_stub(mock_server):
    stub = Stub(Predicate(path="/test1"), Response(body="sausages"))
    port = 4567
    with mock_server([]) as s:
        logger.debug("server: %s", s)
        mock_server.add_stabs(port, stub)
        imposter = mock_server.get_imposter_by_port(port)
        r1 = requests.get(f"{imposter.url}/test1")
    assert_that(r1, is_response().with_body("sausages"))


def test_not_existing_imposter_multiple_stubs(mock_server):
    stubs = [
        Stub(Predicate(path="/test1"), Response(body="sausages")),
        Stub(Predicate(path="/test2"), Response(body="chips")),
    ]
    port = 4567
    with mock_server([]) as s:
        logger.debug("server: %s", s)
        mock_server.add_stabs(port, stubs)
        imposter = mock_server.get_imposter_by_port(port)
        r1 = requests.get(f"{imposter.url}/test1")
        r2 = requests.get(f"{imposter.url}/test2")
    assert_that(r1, is_response().with_body("sausages"))
    assert_that(r2, is_response().with_body("chips"))


def test_existing_imposter_multiple_stubs(mock_server):
    existing_imposter = Imposter(
        [
            Stub(Predicate(path="/test1"), Response(body="response1")),
            Stub(Predicate(path="/test2"), Response(body="response2")),
        ],
        port=4567,
        name="bill",
    )
    stubs = [
        Stub(Predicate(path="/test3"), Response(body="response3")),
        Stub(Predicate(path="/test4"), Response(body="response4")),
    ]
    with mock_server(existing_imposter) as s:
        logger.debug("server: %s", s)
        mock_server.add_stabs(existing_imposter.port, stubs)
        imposter = mock_server.get_imposter_by_port(existing_imposter.port)
        responses = [requests.get(f"{imposter.url}/test{i}") for i in range(1, 5)]
    for number, response in enumerate(responses, start=1):
        assert_that(response, is_response().with_body(f"response{number}"))
