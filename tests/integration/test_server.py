# encoding=utf-8
from __future__ import unicode_literals, absolute_import, division, print_function

import logging

import requests
from brunns.matchers.response import response_with
from hamcrest import assert_that, is_

from mbtest.imposters import Imposter, Predicate, Response, Stub
from mbtest.matchers import had_request

logger = logging.getLogger(__name__)


def test_request_to_mock_server(mock_server):
    # Start mock server with required behavior
    imposter = Imposter(Stub(Predicate(path="/test"), Response(body="sausages")))

    with mock_server(imposter) as server:
        # Make request to mock server
        response = requests.get("{0}/test".format(imposter.url))

        assert_that("We got the expected response", response, is_(response_with(status_code=200, body="sausages")))
        assert_that("The mock server recorded the request", server, had_request(path="/test", method="GET"))
