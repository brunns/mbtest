# encoding=utf-8
import logging

import pytest
import requests
from brunns.matchers.html import has_title
from brunns.matchers.object import between
from brunns.matchers.response import is_response
from contexttimer import Timer
from hamcrest import assert_that, has_entry
from mbtest.imposters import Imposter, Predicate, Proxy, Stub
from mbtest.matchers import had_request
from tests.utils.network import internet_connection

logger = logging.getLogger(__name__)

INTERNET_CONNECTED = internet_connection()


@pytest.mark.skipif(not INTERNET_CONNECTED, reason="No internet connection.")
def test_proxy(mock_server):
    imposter = Imposter(Proxy(to="http://example.com"))

    with mock_server(imposter) as server:
        response = requests.get(imposter.url)

        assert_that(
            response, is_response().with_status_code(200).and_body(has_title("Example Domain"))
        )
        assert_that(server, had_request().with_path("/").and_method("GET"))


@pytest.mark.skipif(not INTERNET_CONNECTED, reason="No internet connection.")
def test_proxy_in_stub(mock_server):
    imposter = Imposter(Stub(responses=Proxy(to="http://example.com")))

    with mock_server(imposter):
        response = requests.get(imposter.url)

        assert_that(
            response, is_response().with_status_code(200).and_body(has_title("Example Domain"))
        )


def test_proxy_delay(mock_server):
    target_imposter = Imposter(Stub(Predicate(path="/test")))
    with mock_server(target_imposter) as server:
        proxy_imposter = Imposter(Stub(responses=Proxy(to=target_imposter.url, wait=100)))
        server.add_imposters(proxy_imposter)

        with Timer() as timer:
            requests.get(proxy_imposter.url / "test")

            assert_that(timer.elapsed, between(0.1, 0.15))


def test_inject_headers(mock_server):
    target_imposter = Imposter(Stub(Predicate(path="/test")))
    with mock_server(target_imposter) as server:
        proxy_imposter = Imposter(
            Stub(
                responses=Proxy(
                    to=target_imposter.url,
                    inject_headers={"X-Clacks-Overhead": "GNU Terry Pratchett"},
                )
            )
        )
        server.add_imposters(proxy_imposter)

        requests.get(proxy_imposter.url / "test")
        assert_that(
            server,
            had_request()
            .with_path("/test")
            .and_headers(has_entry("X-Clacks-Overhead", "GNU Terry Pratchett")),
        )
