# encoding=utf-8
from __future__ import unicode_literals, absolute_import, division, print_function

import logging

import requests
from brunns.matchers.response import response_with
from contexttimer import Timer
from hamcrest import assert_that, is_, close_to

from mbtest.imposters import Imposter, Stub, Predicate, Response

logger = logging.getLogger(__name__)


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
