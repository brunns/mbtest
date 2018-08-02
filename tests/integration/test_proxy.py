import logging

import pytest
import requests
from brunns.matchers.response import response_with
from hamcrest import assert_that, is_, contains_string

from mbtest.imposters import Imposter, Proxy
from mbtest.matchers import had_request

logger = logging.getLogger(__name__)


@pytest.mark.usefixtures("mock_server")
def test_proxy(mock_server):
    # Start mock server with required behavior
    imposter = Imposter(Proxy(to="http://example.com"), record_requests=True)

    with mock_server(imposter) as server:
        # Make request to mock server
        response = requests.get("{0}/".format(imposter.url))

        assert_that(response, is_(response_with(status_code=200, body=contains_string("<h1>Example Domain</h1>"))))
        assert_that(server, had_request(path="/", method="GET"))
