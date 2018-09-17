# encoding=utf-8
from __future__ import unicode_literals, absolute_import, division, print_function

import logging

import pytest
import requests
from brunns.matchers.html import has_title
from brunns.matchers.object import between
from brunns.matchers.response import response_with
from contexttimer import Timer
from hamcrest import assert_that, is_

from mbtest.imposters import Imposter, Proxy
from mbtest.matchers import had_request

logger = logging.getLogger(__name__)


@pytest.mark.usefixtures("mock_server")
def test_proxy(mock_server):
    imposter = Imposter(Proxy(to="http://example.com"))

    with mock_server(imposter) as server:
        response = requests.get("{0}/".format(imposter.url))

        assert_that(response, is_(response_with(status_code=200, body=has_title("Example Domain"))))
        assert_that(server, had_request(path="/", method="GET"))


@pytest.mark.usefixtures("mock_server")
def test_proxy_delay(mock_server):
    imposter = Imposter(Proxy(to="http://example.com", wait=500))

    with mock_server(imposter), Timer() as t:
        requests.get("{0}/".format(imposter.url))

    assert_that(
        t.elapsed, between(0.5, 0.9)
    )  # Slightly longer than the wait time, to give example.com and the 'net time to work.
