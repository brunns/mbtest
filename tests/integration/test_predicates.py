# encoding=utf-8
import logging

import pytest
import requests
from brunns.matchers.response import response_with
from hamcrest import assert_that, is_, not_

from mbtest.imposters import Imposter, Stub, Predicate, Response

logger = logging.getLogger(__name__)


def test_and_predicate_and_query_strings(mock_server):
    imposter = Imposter(
        Stub(Predicate(query={"foo": "bar"}) & Predicate(query={"dinner": "chips"}), Response(body="black pudding"))
    )

    with mock_server(imposter) as s:
        logger.debug("server: %s", s)

        r1 = requests.get("{0}/".format(imposter.url), params={"dinner": "chips", "foo": "bar"})
        r2 = requests.get("{0}/".format(imposter.url), params={"dinner": "chips"})

        assert_that(r1, is_(response_with(status_code=200, body="black pudding")))
        assert_that(r2, not_(response_with(status_code=200, body="black pudding")))


def test_or_predicate_and_body(mock_server):
    imposter = Imposter(Stub(Predicate(body="foo") | Predicate(body="bar"), Response(body="oranges")))

    with mock_server(imposter) as s:
        logger.debug("server: %s", s)

        r1 = requests.get(imposter.url, data="foo")
        r2 = requests.get(imposter.url, data="bar")
        r3 = requests.get(imposter.url, data="baz")

        assert_that(r1, is_(response_with(status_code=200, body="oranges")))
        assert_that(r2, is_(response_with(status_code=200, body="oranges")))
        assert_that(r3, not_(response_with(status_code=200, body="oranges")))


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
        assert_that(r1, is_(response_with(body="oranges")))
        assert_that(r2, is_(response_with(body=not_("oranges"))))
        assert_that(r3, is_(response_with(body=not_("oranges"))))


def test_methods(mock_server):
    # Given
    imposter = Imposter(
        [
            Stub(Predicate(method=Predicate.Method.GET), Response(body="get")),
            Stub(Predicate(method=Predicate.Method.PUT), Response(body="put")),
            Stub(Predicate(method=Predicate.Method.POST), Response(body="post")),
            Stub(Predicate(method=Predicate.Method.DELETE), Response(body="delete")),
        ]
    )

    with mock_server(imposter) as s:
        logger.debug("server: %s", s)

        # When
        delete = requests.delete(imposter.url)
        post = requests.post(imposter.url)
        put = requests.put(imposter.url)
        get = requests.get(imposter.url)

        # Then
        assert_that(delete, is_(response_with(body="delete")))
        assert_that(post, is_(response_with(body="post")))
        assert_that(put, is_(response_with(body="put")))
        assert_that(get, is_(response_with(body="get")))


def test_structure_path():
    expected_predicate = Predicate(path="/darwin")
    predicate_structure = expected_predicate.as_structure()
    predicate = Predicate.from_structure(predicate_structure)
    assert predicate.path == expected_predicate.path


def test_structure_body():
    expected_predicate = Predicate(body="darwin")
    predicate_structure = expected_predicate.as_structure()
    predicate = Predicate.from_structure(predicate_structure)
    assert predicate.body == expected_predicate.body


def test_structure_method():
    expected_predicate = Predicate(method="GET")
    predicate_structure = expected_predicate.as_structure()
    predicate = Predicate.from_structure(predicate_structure)
    assert predicate.method == expected_predicate.method


def test_structure_query():
    expected_predicate = Predicate(query={"key": "value"})
    predicate_structure = expected_predicate.as_structure()
    predicate = Predicate.from_structure(predicate_structure)
    assert predicate.query == expected_predicate.query


def test_structure_operator():
    expected_predicate = Predicate(operator="deepEquals")
    predicate_structure = expected_predicate.as_structure()
    predicate = Predicate.from_structure(predicate_structure)
    assert predicate.operator == expected_predicate.operator


def test_structure_xpath():
    expected_predicate = Predicate(xpath="darwin")
    predicate_structure = expected_predicate.as_structure()
    predicate = Predicate.from_structure(predicate_structure)
    assert predicate.xpath == expected_predicate.xpath


def test_invalid_operator():
    expected_predicate = Predicate(operator="deepEquals")
    predicate_structure = expected_predicate.as_structure()
    # Adds another operator
    predicate_structure["equals"] = {}
    with pytest.raises(Predicate.InvalidPredicateOperator):
        Predicate.from_structure(predicate_structure)
