# encoding=utf-8
import logging
import os
from decimal import Decimal

import pytest
import requests
from brunns.matchers.response import is_response
from hamcrest import assert_that, not_
from mbtest.imposters import Imposter, InjectionPredicate, Predicate, Response, Stub

logger = logging.getLogger(__name__)


def test_and_predicate_and_query_strings(mock_server):
    imposter = Imposter(
        Stub(
            Predicate(query={"foo": "bar"}) & Predicate(query={"dinner": "chips"}),
            Response(body="black pudding"),
        )
    )

    with mock_server(imposter) as s:
        logger.debug("server: %s", s)

        r1 = requests.get("{0}/".format(imposter.url), params={"dinner": "chips", "foo": "bar"})
        r2 = requests.get("{0}/".format(imposter.url), params={"dinner": "chips"})

        assert_that(r1, is_response().with_status_code(200).and_body("black pudding"))
        assert_that(r2, not_(is_response().with_status_code(200).and_body("black pudding")))


def test_or_predicate_and_body(mock_server):
    imposter = Imposter(
        Stub(Predicate(body="foo") | Predicate(body="bar"), Response(body="oranges"))
    )

    with mock_server(imposter) as s:
        logger.debug("server: %s", s)

        r1 = requests.get(imposter.url, data="foo")
        r2 = requests.get(imposter.url, data="bar")
        r3 = requests.get(imposter.url, data="baz")

        assert_that(r1, is_response().with_status_code(200).and_body("oranges"))
        assert_that(r2, is_response().with_status_code(200).and_body("oranges"))
        assert_that(r3, not_(is_response().with_status_code(200).and_body("oranges")))


def test_query_predicate(mock_server):
    # Given
    imposter = Imposter(Stub(Predicate(query={"foo": "bar"}), Response(body="oranges")))

    with mock_server(imposter) as s:
        logger.debug("server: %s", s)

        # When
        r1 = requests.get(imposter.url, params={"foo": "bar"})
        r2 = requests.get(imposter.url, params={"foo": "baz"})
        r3 = requests.get(imposter.url)

        # Then
        assert_that(r1, is_response().with_body("oranges"))
        assert_that(r2, is_response().with_body(not_("oranges")))
        assert_that(r3, is_response().with_body(not_("oranges")))


def test_headers_predicate(mock_server):
    # Given
    imposter = Imposter(Stub(Predicate(headers={"foo": "bar"}), Response(body="oranges")))

    with mock_server(imposter) as s:
        logger.debug("server: %s", s)

        # When
        r1 = requests.get(imposter.url, headers={"foo": "bar"})
        r2 = requests.get(imposter.url, headers={"foo": "baz"})
        r3 = requests.get(imposter.url)

        # Then
        assert_that(r1, is_response().with_body("oranges"))
        assert_that(r2, is_response().with_body(not_("oranges")))
        assert_that(r3, is_response().with_body(not_("oranges")))


def test_methods(mock_server):
    # Given
    imposter = Imposter(
        [
            Stub(Predicate(method=Predicate.Method.GET), Response(body="get")),
            Stub(Predicate(method=Predicate.Method.PUT), Response(body="put")),
            Stub(Predicate(method=Predicate.Method.POST), Response(body="post")),
            Stub(Predicate(method=Predicate.Method.DELETE), Response(body="delete")),
            Stub(Predicate(method=Predicate.Method.PATCH), Response(body="patch")),
            Stub(Predicate(method=Predicate.Method.HEAD), Response(status_code=789)),
        ]
    )

    with mock_server(imposter) as s:
        logger.debug("server: %s", s)

        # When
        delete = requests.delete(imposter.url)
        post = requests.post(imposter.url)
        put = requests.put(imposter.url)
        patch = requests.patch(imposter.url)
        get = requests.get(imposter.url)
        head = requests.head(imposter.url)

        # Then
        assert_that(delete, is_response().with_body("delete"))
        assert_that(post, is_response().with_body("post"))
        assert_that(put, is_response().with_body("put"))
        assert_that(patch, is_response().with_body("patch"))
        assert_that(get, is_response().with_body("get"))
        assert_that(head, is_response().with_status_code(789))


@pytest.mark.skipif(
    Decimal(os.environ.get("MBTEST_VERSION", "2.0")) < 2,
    reason="Injection requires Mountebank version 2.0 or higher.",
)
def test_injection_predicate(mock_server):
    # Given
    imposter = Imposter(
        Stub(
            InjectionPredicate(
                inject="function (config) {return config.request.headers['foo'] === 'bar'}"
            ),
            Response(body="matched"),
        )
    )

    with mock_server(imposter) as s:
        logger.debug("server: %s", s)

        # When
        r1 = requests.get(imposter.url, headers={"foo": "bar"})
        r2 = requests.get(imposter.url, headers={"foo": "baz"})

        # Then
        assert_that(r1, is_response().with_body("matched"))
        assert_that(r2, is_response().with_body(not_("matched")))
