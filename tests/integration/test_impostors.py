# encoding=utf-8
import logging

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

        assert_that(
            response, is_response().with_status_code(200).and_body("sausages"),
        )
        assert_that(
            imposter, had_request().with_path("/test").and_method("GET"),
        )
