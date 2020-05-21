# encoding=utf-8
import logging

import pytest
import requests
from brunns.matchers.data import json_matching
from brunns.matchers.html import has_title
from brunns.matchers.object import between
from brunns.matchers.response import is_response
from contexttimer import Timer
from hamcrest import assert_that, contains_string, has_entries, has_entry
from mbtest.imposters import Imposter, Predicate, Proxy, Stub
from mbtest.imposters.responses import PredicateGenerator
from mbtest.matchers import had_request
from tests.utils.network import internet_connection

logger = logging.getLogger(__name__)

INTERNET_CONNECTED = internet_connection()


@pytest.mark.skipif(not INTERNET_CONNECTED, reason="No internet connection.")
def test_proxy(mock_server):
    imposter = Imposter(Stub(responses=Proxy(to="http://example.com")))

    with mock_server(imposter):
        response = requests.get(imposter.url)

        assert_that(
            response, is_response().with_status_code(200).and_body(has_title("Example Domain"))
        )
        assert_that(imposter, had_request().with_path("/").and_method("GET"))


@pytest.mark.skipif(not INTERNET_CONNECTED, reason="No internet connection.")
def test_proxy_playback(mock_server):
    proxy_imposter = Imposter(Stub(responses=Proxy(to="https://httpbin.org", mode=Proxy.Mode.ONCE)))

    with mock_server(proxy_imposter):
        response = requests.get(proxy_imposter.url / "status/418")
        assert_that(
            response, is_response().with_status_code(418).and_body(contains_string("teapot"))
        )
        response = requests.get(proxy_imposter.url / "status/200")
        assert_that(
            response, is_response().with_status_code(418).and_body(contains_string("teapot"))
        )

        recorded_stubs = proxy_imposter.playback()

    playback_impostor = Imposter(recorded_stubs)
    with mock_server(playback_impostor):
        response = requests.get(playback_impostor.url)
        assert_that(
            response, is_response().with_status_code(418).and_body(contains_string("teapot"))
        )


@pytest.mark.skipif(not INTERNET_CONNECTED, reason="No internet connection.")
def test_proxy_uses_path_predicate_generator(mock_server):
    proxy_imposter = Imposter(
        Stub(
            responses=Proxy(
                to="https://httpbin.org",
                mode=Proxy.Mode.ONCE,
                predicate_generators=[PredicateGenerator(path=True)],
            )
        )
    )

    with mock_server(proxy_imposter):
        response = requests.get(proxy_imposter.url / "status/418")
        assert_that(
            response, is_response().with_status_code(418).and_body(contains_string("teapot"))
        )
        response = requests.get(proxy_imposter.url / "status/200")
        assert_that(response, is_response().with_status_code(200))

        recorded_stubs = proxy_imposter.playback()

    playback_impostor = Imposter(recorded_stubs)
    with mock_server(playback_impostor):
        response = requests.get(playback_impostor.url / "status/418")
        assert_that(
            response, is_response().with_status_code(418).and_body(contains_string("teapot"))
        )
        response = requests.get(playback_impostor.url / "status/200")
        assert_that(response, is_response().with_status_code(200))


@pytest.mark.skipif(not INTERNET_CONNECTED, reason="No internet connection.")
def test_proxy_uses_query_predicate_generator(mock_server):
    proxy_imposter = Imposter(
        Stub(
            responses=Proxy(
                to="https://httpbin.org",
                mode=Proxy.Mode.ONCE,
                predicate_generators=[PredicateGenerator(query=True)],
            )
        )
    )

    with mock_server(proxy_imposter):
        response = requests.get(proxy_imposter.url / "get", params={"foo": "bar"})
        assert_that(
            response,
            is_response().with_body(json_matching(has_entries(args=has_entries(foo="bar")))),
        )
        response = requests.get(proxy_imposter.url / "get", params={"foo": "baz"})
        assert_that(
            response,
            is_response().with_body(json_matching(has_entries(args=has_entries(foo="baz")))),
        )

        recorded_stubs = proxy_imposter.playback()

    playback_impostor = Imposter(recorded_stubs)
    with mock_server(playback_impostor):
        response = requests.get(playback_impostor.url / "get", params={"foo": "bar"})
        assert_that(
            response,
            is_response().with_body(json_matching(has_entries(args=has_entries(foo="bar")))),
        )
        response = requests.get(playback_impostor.url / "get", params={"foo": "baz"})
        assert_that(
            response,
            is_response().with_body(json_matching(has_entries(args=has_entries(foo="baz")))),
        )


@pytest.mark.skipif(not INTERNET_CONNECTED, reason="No internet connection.")
def test_proxy_without_stub(mock_server):
    imposter = Imposter(Proxy(to="http://example.com"))

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

            assert_that(timer.elapsed, between(0.1, 0.2))


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
            target_imposter,
            had_request()
            .with_path("/test")
            .and_headers(has_entry("X-Clacks-Overhead", "GNU Terry Pratchett")),
        )
