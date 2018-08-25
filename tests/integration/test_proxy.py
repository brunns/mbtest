import logging

import pytest
import requests
from brunns.matchers.html import has_title
from brunns.matchers.response import response_with
from contexttimer import Timer
from hamcrest import assert_that, is_, close_to

from mbtest.imposters import Imposter, Proxy
from mbtest.matchers import had_request

logger = logging.getLogger(__name__)


@pytest.mark.usefixtures("mock_server")
def test_proxy(mock_server):
    imposter = Imposter(Proxy(to="http://example.com"), record_requests=True)

    with mock_server(imposter) as server:
        response = requests.get("{0}/".format(imposter.url))

        assert_that(response, is_(response_with(status_code=200, body=has_title("Example Domain"))))
        assert_that(server, had_request(path="/", method="GET"))


@pytest.mark.usefixtures("mock_server")
def test_proxy_delay(mock_server):
    imposter = Imposter(Proxy(to="http://example.com", wait=500), record_requests=True)

    with mock_server(imposter):
        with Timer() as t:
            requests.get("{0}/".format(imposter.url))

    assert_that(
        t.elapsed, close_to(0.6, 0.2)
    )  # Slightly longer than the wait time, to give example.com and the 'net time to work.
