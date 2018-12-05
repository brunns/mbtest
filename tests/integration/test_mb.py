# encoding=utf-8
from __future__ import unicode_literals, absolute_import, division, print_function

import logging

import pytest
import requests
from brunns.matchers.response import response_with
from hamcrest import assert_that, is_

from mbtest.imposters import Imposter, Predicate, Response, Stub
from mbtest.matchers import had_request

logger = logging.getLogger(__name__)


@pytest.mark.usefixtures("mock_server")
def test_request_to_mock_server(mock_server):
    # Start mock server with required behavior
    imposter = Imposter(Stub(Predicate(path="/test"), Response(body="sausages")))

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
def test_multiple_stubs(mock_server):
    imposter = Imposter(
        [
            Stub(Predicate(path="/test1"), Response(body="sausages")),
            Stub(Predicate(path="/test2"), Response(body="chips")),
        ],
        port=4567,
        name="bill",
    )

    with mock_server(imposter) as s:
        logger.debug("server: %s", s)
        r1 = requests.get("{0}/test1".format(imposter.url))
        r2 = requests.get("{0}/test2".format(imposter.url))

        pass
    assert_that(r1, response_with(body="sausages"))
    assert_that(r2, response_with(body="chips"))


@pytest.mark.usefixtures("mock_server")
def test_default_imposter(mock_server):
    imposter = Imposter(Stub())

    with mock_server(imposter) as s:
        logger.debug("server: %s", s)
        r = requests.get("{0}/".format(imposter.url))

    assert_that(r, response_with(status_code=200, body=""))
