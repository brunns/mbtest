# encoding=utf-8
import logging
import os

import pytest
import requests
from brunns.matchers.response import is_response
from hamcrest import assert_that

from mbtest.imposters import Imposter, Predicate, Response, Stub
from mbtest.matchers import had_request

logger = logging.getLogger(__name__)


def test_multiple_imposters(mock_server):
    imposters = [
        Imposter(Stub(Predicate(path="/test1"), Response("sausages"))),
        Imposter([Stub([Predicate(path="/test2")], [Response("chips", status_code=201)])]),
    ]

    with mock_server(imposters):
        r1 = requests.get(f"{imposters[0].url}/test1")
        r2 = requests.get(f"{imposters[1].url}/test2")

    assert_that(r1, is_response().with_status_code(200).and_body("sausages"))
    assert_that(r2, is_response().with_status_code(201).and_body("chips"))


def test_default_imposter(mock_server):
    imposter = Imposter(Stub())

    with mock_server(imposter):
        r = requests.get(f"{imposter.url}/")

    assert_that(r, is_response().with_status_code(200).and_body(""))


def test_imposter_had_request_matcher(mock_server):
    imposter = Imposter(Stub(Predicate(path="/test"), Response(body="sausages")))

    with mock_server(imposter):
        response = requests.get(f"{imposter.url}/test")

        assert_that(response, is_response().with_status_code(200).and_body("sausages"))
        assert_that(imposter, had_request().with_path("/test").and_method("GET"))


@pytest.mark.skipif(
    float(os.environ.get("MBTEST_VERSION", "2.1")) < 2.1,
    reason="AddStubs to existing imposter requires Mountebank version 2.1 or higher.",
)
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
        existing_imposter.add_stubs(stubs)
        responses = [requests.get(f"{existing_imposter.url}/test{i}") for i in range(1, 5)]
    for number, response in enumerate(responses, start=1):
        assert_that(response, is_response().with_body(f"response{number}"))
