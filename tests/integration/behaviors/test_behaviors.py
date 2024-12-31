import logging

import httpx
from brunns.matchers.object import between
from brunns.matchers.response import is_response
from contexttimer import Timer
from hamcrest import assert_that

from mbtest.imposters import Imposter, Predicate, Response, Stub

logger = logging.getLogger(__name__)


def test_wait(mock_server):
    imposter = Imposter(Stub(responses=Response(wait=100)))

    with mock_server(imposter), Timer() as timer:
        httpx.get(str(imposter.url))

        assert_that(timer.elapsed, between(0.1, 0.3))


def test_wait_function(mock_server):
    imposter = Imposter(Stub(responses=Response(wait="function() { return Math.floor(Math.random() * 50) + 100; }")))

    with mock_server(imposter), Timer() as timer:
        httpx.get(str(imposter.url))

        assert_that(timer.elapsed, between(0.1, 0.5))


def test_repeat(mock_server):
    # Given
    imposter = Imposter(Stub(Predicate(), [Response(body="oranges", repeat=2), Response(body="apples")]))

    with mock_server(imposter) as s:
        logger.debug("server: %s", s)

        # When
        r1 = httpx.get(str(imposter.url))
        r2 = httpx.get(str(imposter.url))
        r3 = httpx.get(str(imposter.url))

        # Then
        assert_that(r1, is_response().with_body("oranges"))
        assert_that(r2, is_response().with_body("oranges"))
        assert_that(r3, is_response().with_body("apples"))
