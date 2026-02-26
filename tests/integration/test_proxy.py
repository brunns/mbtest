import logging
import os
import platform

import httpx
import pytest
from brunns.matchers.data import json_matching
from brunns.matchers.html import has_title
from brunns.matchers.object import between
from brunns.matchers.response import is_response
from contexttimer import Timer
from hamcrest import assert_that, contains_string, has_entries, has_entry

from mbtest.imposters import Imposter, Predicate, Proxy, Stub
from mbtest.imposters.responses import PredicateGenerator, Response
from mbtest.matchers import had_request
from tests.utils.network import internet_connection

logger = logging.getLogger(__name__)

INTERNET_CONNECTED = internet_connection()
LOCAL = os.getenv("GITHUB_ACTIONS") != "true"
LINUX = platform.system() == "Linux"
HTTPBIN_CONTAINERISED = LINUX or LOCAL


@pytest.mark.xfail(not HTTPBIN_CONTAINERISED, reason="Public httpbin horribly flaky.")
def test_proxy(mock_server, httpbin):
    imposter = Imposter(Stub(responses=Proxy(to=httpbin)))

    with mock_server(imposter):
        response = httpx.get(str(imposter.url))

        assert_that(response, is_response().with_status_code(200).and_body(has_title("httpbin.org")))
        assert_that(imposter, had_request().with_path("/").and_method("GET"))


@pytest.mark.xfail(not HTTPBIN_CONTAINERISED, reason="Public httpbin horribly flaky.")
def test_stub_with_proxy_fallback(mock_server, httpbin):
    imposter = Imposter(
        stubs=[
            Stub(Predicate(path="/test"), Response(body="sausages")),
            Stub(responses=Proxy(to=httpbin, mode=Proxy.Mode.TRANSPARENT)),
        ]
    )

    with mock_server(imposter):
        response = httpx.get(str(imposter.url / "test"))
        assert_that(response, is_response().with_status_code(200).and_body("sausages"))

        response = httpx.get(str(imposter.url))
        assert_that(response, is_response().with_status_code(200).and_body(has_title("httpbin.org")))
        assert_that(imposter, had_request().with_path("/").and_method("GET"))


@pytest.mark.xfail(not HTTPBIN_CONTAINERISED, reason="Public httpbin horribly flaky.")
def test_proxy_playback(mock_server, httpbin):
    proxy_imposter = Imposter(Stub(responses=Proxy(to=httpbin, mode=Proxy.Mode.ONCE)))

    with mock_server(proxy_imposter):
        response = httpx.get(str(proxy_imposter.url / "status/418"))
        assert_that(response, is_response().with_status_code(418).and_body(contains_string("teapot")))
        response = httpx.get(str(proxy_imposter.url / "status/200"))
        assert_that(response, is_response().with_status_code(418).and_body(contains_string("teapot")))

        recorded_stubs = proxy_imposter.playback()

    playback_impostor = Imposter(recorded_stubs)
    with mock_server(playback_impostor):
        response = httpx.get(str(playback_impostor.url))
        assert_that(response, is_response().with_status_code(418).and_body(contains_string("teapot")))


@pytest.mark.xfail(not HTTPBIN_CONTAINERISED, reason="Public httpbin horribly flaky.")
def test_proxy_uses_path_predicate_generator(mock_server, httpbin):
    proxy_imposter = Imposter(
        Stub(
            responses=Proxy(
                to=httpbin,
                mode=Proxy.Mode.ONCE,
                predicate_generators=[PredicateGenerator(path=True)],
            )
        )
    )

    with mock_server(proxy_imposter):
        response = httpx.get(str(proxy_imposter.url / "status/418"))
        assert_that(response, is_response().with_status_code(418).and_body(contains_string("teapot")))
        response = httpx.get(str(proxy_imposter.url / "status/200"))
        assert_that(response, is_response().with_status_code(200))

        recorded_stubs = proxy_imposter.playback()

    playback_impostor = Imposter(recorded_stubs)
    with mock_server(playback_impostor):
        response = httpx.get(str(playback_impostor.url / "status/418"))
        assert_that(response, is_response().with_status_code(418).and_body(contains_string("teapot")))
        response = httpx.get(str(playback_impostor.url / "status/200"))
        assert_that(response, is_response().with_status_code(200))


@pytest.mark.xfail(not HTTPBIN_CONTAINERISED, reason="Public httpbin horribly flaky.")
def test_proxy_uses_query_predicate_generator(mock_server, httpbin):
    proxy_imposter = Imposter(
        Stub(
            responses=Proxy(
                to=httpbin,
                mode=Proxy.Mode.ONCE,
                predicate_generators=[PredicateGenerator(query=True)],
            )
        )
    )

    with mock_server(proxy_imposter):
        response = httpx.get(str(proxy_imposter.url / "get"), params={"foo": "bar"})
        assert_that(response, is_response().with_body(json_matching(has_entries(args=has_entries(foo="bar")))))
        response = httpx.get(str(proxy_imposter.url / "get"), params={"foo": "baz"})
        assert_that(response, is_response().with_body(json_matching(has_entries(args=has_entries(foo="baz")))))

        recorded_stubs = proxy_imposter.playback()

    playback_impostor = Imposter(recorded_stubs)
    with mock_server(playback_impostor):
        response = httpx.get(str(playback_impostor.url / "get"), params={"foo": "bar"})
        assert_that(response, is_response().with_body(json_matching(has_entries(args=has_entries(foo="bar")))))
        response = httpx.get(str(playback_impostor.url / "get"), params={"foo": "baz"})
        assert_that(response, is_response().with_body(json_matching(has_entries(args=has_entries(foo="baz")))))


@pytest.mark.xfail(not HTTPBIN_CONTAINERISED, reason="Public httpbin horribly flaky.")
def test_proxy_uses_query_predicate_generator_with_key(mock_server, httpbin):
    proxy_imposter = Imposter(
        Stub(
            responses=Proxy(
                to=httpbin,
                mode=Proxy.Mode.ONCE,
                predicate_generators=[PredicateGenerator(query={"foo": "whatever"})],
            )
        )
    )

    with mock_server(proxy_imposter):
        response = httpx.get(str(proxy_imposter.url / "get"), params={"foo": "bar", "quxx": "buzz"})
        assert_that(
            response, is_response().with_body(json_matching(has_entries(args=has_entries(foo="bar", quxx="buzz"))))
        )
        response = httpx.get(str(proxy_imposter.url / "get"), params={"foo": "baz", "quxx": "buxx"})
        assert_that(response, is_response().with_body(json_matching(has_entries(args=has_entries(foo="baz")))))

        recorded_stubs = proxy_imposter.playback()

    playback_impostor = Imposter(recorded_stubs)
    with mock_server(playback_impostor):
        response = httpx.get(str(playback_impostor.url / "get"), params={"foo": "bar", "quxx": "whatever"})
        assert_that(
            response, is_response().with_body(json_matching(has_entries(args=has_entries(foo="bar", quxx="buzz"))))
        )
        response = httpx.get(str(playback_impostor.url / "get"), params={"foo": "baz", "quxx": "anything"})
        assert_that(
            response, is_response().with_body(json_matching(has_entries(args=has_entries(foo="baz", quxx="buxx"))))
        )


@pytest.mark.xfail(not HTTPBIN_CONTAINERISED, reason="Public httpbin horribly flaky.")
def test_proxy_without_stub(mock_server, httpbin):
    imposter = Imposter(Stub(responses=Proxy(to=httpbin)))

    with mock_server(imposter):
        response = httpx.get(str(imposter.url))

        assert_that(response, is_response().with_status_code(200).and_body(has_title("httpbin.org")))


@pytest.mark.xfail(not HTTPBIN_CONTAINERISED, reason="Public httpbin horribly flaky.")
def test_record_and_replay_via_server(mock_server, httpbin, tmp_path):
    """Proxy requests through Mountebank, then retrieve as a replayable imposter and save/load from file."""
    proxy_imposter = Imposter(Stub(responses=Proxy(to=httpbin, mode=Proxy.Mode.ONCE)))

    with mock_server(proxy_imposter) as server:
        httpx.get(str(proxy_imposter.url / "status/418"))
        replayable = server.get_replayable_imposter(proxy_imposter)

    assert replayable.port == proxy_imposter.port
    assert len(replayable.stubs) > 0

    saved = tmp_path / "recorded.json"
    replayable.save(saved)
    loaded = Imposter.from_file(saved)
    assert loaded.port == replayable.port

    with mock_server(loaded):
        response = httpx.get(str(loaded.url / "status/418"))
        assert_that(response, is_response().with_status_code(418).and_body(contains_string("teapot")))


@pytest.mark.xfail(not HTTPBIN_CONTAINERISED, reason="Public httpbin horribly flaky.")
def test_proxy_delay(mock_server):
    target_imposter = Imposter(Stub(Predicate(path="/test")))
    with mock_server(target_imposter) as server:
        proxy_imposter = Imposter(Stub(responses=Proxy(to=target_imposter.url, wait=100)))
        server.add_imposters(proxy_imposter)

        with Timer() as timer:
            httpx.get(str(proxy_imposter.url / "test"))

            assert_that(timer.elapsed, between(0.1, 0.5))


@pytest.mark.xfail(not HTTPBIN_CONTAINERISED, reason="Public httpbin horribly flaky.")
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

        httpx.get(str(proxy_imposter.url / "test"))
        assert_that(
            target_imposter,
            had_request().with_path("/test").and_headers(has_entry("X-Clacks-Overhead", "GNU Terry Pratchett")),
        )
