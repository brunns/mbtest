import logging

import pytest
import requests
from hamcrest import assert_that, is_

from matchers.request import had_request
from matchers.response import has_body_containing, has_status_code, response_with
from mb.imposters import Imposter, Predicate, Response, Stub

logger = logging.getLogger(__name__)


@pytest.mark.usefixtures("mock_server")
def test_request_to_mock_server(mock_server):
    # Start mock server with required behavior
    imposter = Imposter(Stub(Predicate(path="/test"), Response(body="sausages")), record_requests=True)

    with mock_server(imposter) as server:
        # Make request to mock server
        response = requests.get("{}/test".format(imposter.url))

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
        r1 = requests.get("{}/test1".format(imposters[0].url))
        r2 = requests.get("{}/test2".format(imposters[1].url))

    assert_that(r1, has_status_code(200))
    assert_that(r1, has_body_containing("sausages"))
    assert_that(r2, has_status_code(201))
    assert_that(r2, has_body_containing("chips"))


@pytest.mark.usefixtures("mock_server")
def test_default_imposter(mock_server):
    imposter = Imposter(Stub())

    with mock_server(imposter) as s:
        logger.debug("server: %s", s)
        r = requests.get("{}/".format(imposter.url))

    assert_that(r, response_with(status_code=200, body=""))
