import logging

import httpx
from brunns.matchers.data import json_matching
from brunns.matchers.response import is_response
from hamcrest import assert_that, not_

from mbtest.imposters import Imposter, Predicate, Response, Stub

logger = logging.getLogger(__name__)


def test_json_payload(mock_server):
    # Given
    imposter = Imposter(Stub(Predicate(body={"foo": ["bar", "baz"]}), Response(body="sausages")))

    with mock_server(imposter):
        # When
        r1 = httpx.post(str(imposter.url), json={"foo": ["bar", "baz"]})
        r2 = httpx.post(str(imposter.url), json={"baz": ["bar", "foo"]})

        # Then
        assert_that(r1, is_response().with_body("sausages"))
        assert_that(r2, not_(is_response().with_body("sausages")))


def test_json_response(mock_server):
    # Given
    imposter = Imposter(Stub(Predicate(), Response(body={"foo": ["bar", "baz"]})))

    with mock_server(imposter):
        # When
        r = httpx.get(str(imposter.url))

        # Then
        assert_that(r, is_response().with_body(json_matching({"foo": ["bar", "baz"]})))


def test_jsonpath_predicate(mock_server):
    # Given
    imposter = Imposter(
        Stub(
            Predicate(jsonpath="$.foo", body="bar", operator=Predicate.Operator.EQUALS),
            Response(body="sausages"),
        )
    )

    with mock_server(imposter):
        # When
        r1 = httpx.request(method="GET", url=str(imposter.url), json={"foo": "bar"})
        r2 = httpx.request(method="GET", url=str(imposter.url), json={"foo": "baz"})

        # Then
        assert_that(r1, is_response().with_body("sausages"))
        assert_that(r2, is_response().with_body(not_("sausages")))
