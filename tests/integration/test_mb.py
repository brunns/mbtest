import logging

import pytest
import requests
from contexttimer import Timer
from hamcrest import assert_that, is_, not_, close_to

from matchers.response import response_with
from mbtest.imposters import Imposter, Predicate, Response, Stub
from mbtest.matchers import had_request

logger = logging.getLogger(__name__)


@pytest.mark.usefixtures("mock_server")
def test_request_to_mock_server(mock_server):
    # Start mock server with required behavior
    imposter = Imposter(Stub(Predicate(path="/test"), Response(body="sausages")), record_requests=True)

    with mock_server(imposter) as server:
        # Make request to mock server
        response = requests.get("{0}/test".format(imposter.url))

        assert_that("We got the expected response", response, is_(response_with(status_code=200, body="sausages")))
        assert_that("The mock server recorded the request", server, had_request(path="/test", method="GET"))


@pytest.mark.usefixtures("mock_server")
def test_multiple_imposters(mock_server):
    imposters = [
        Imposter(Stub(Predicate(path="/test1"), Response("sausages")), port=4567, name="bill"),
        Imposter([Stub([Predicate(path="/test2")], [Response("chips", status_code=201)])], port=4568),
    ]

    with mock_server(imposters) as s:
        logger.debug("server: %s", s)
        r1 = requests.get("{0}/test1".format(imposters[0].url))
        r2 = requests.get("{0}/test2".format(imposters[1].url))

    assert_that(r1, response_with(status_code=200, body="sausages"))
    assert_that(r2, response_with(status_code=201, body="chips"))


@pytest.mark.usefixtures("mock_server")
def test_default_imposter(mock_server):
    imposter = Imposter(Stub())

    with mock_server(imposter) as s:
        logger.debug("server: %s", s)
        r = requests.get("{0}/".format(imposter.url))

    assert_that(r, response_with(status_code=200, body=""))


@pytest.mark.usefixtures("mock_server")
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


@pytest.mark.usefixtures("mock_server")
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


@pytest.mark.usefixtures("mock_server")
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


@pytest.mark.usefixtures("mock_server")
def test_wait(mock_server):
    # Given
    imposter = Imposter(Stub(Predicate(), Response(body="oranges", wait=500)))

    with mock_server(imposter) as s:
        logger.debug("server: %s", s)

        # When
        with Timer() as t:
            r = requests.get(imposter.url)

        # Then
        assert_that(r, is_(response_with(body="oranges")))
        assert_that(t.elapsed, close_to(0.5, 0.1))


@pytest.mark.usefixtures("mock_server")
def test_repeat(mock_server):
    # Given
    imposter = Imposter(Stub(Predicate(), [Response(body="oranges", repeat=2), Response(body="apples")]))

    with mock_server(imposter) as s:
        logger.debug("server: %s", s)

        # When
        r1 = requests.get(imposter.url)
        r2 = requests.get(imposter.url)
        r3 = requests.get(imposter.url)

        # Then
        assert_that(r1, is_(response_with(body="oranges")))
        assert_that(r2, is_(response_with(body="oranges")))
        assert_that(r3, is_(response_with(body="apples")))
