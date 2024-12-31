import logging
import os
from decimal import Decimal

import httpx
import pytest
from brunns.matchers.data import json_matching
from brunns.matchers.response import is_response
from hamcrest import assert_that, has_entries, has_entry

from mbtest.imposters import Imposter, Response, Stub
from mbtest.imposters.responses import FaultResponse, InjectionResponse

logger = logging.getLogger(__name__)


def test_body(mock_server):
    imposter = Imposter(Stub(responses=Response(body="sausages")))

    with mock_server(imposter):
        response = httpx.get(str(imposter.url))

        assert_that(response, is_response().with_body("sausages"))


def test_status(mock_server):
    imposter = Imposter(Stub(responses=Response(status_code=204)))

    with mock_server(imposter):
        response = httpx.get(str(imposter.url))

        assert_that(response, is_response().with_status_code(204))


def test_headers(mock_server):
    imposter = Imposter(Stub(responses=Response(headers={"X-Clacks-Overhead": "GNU Terry Pratchett"})))

    with mock_server(imposter):
        response = httpx.get(str(imposter.url))

        assert_that(
            response,
            is_response().with_headers(has_entry("x-clacks-overhead", "GNU Terry Pratchett")),
        )


def test_binary_mode(mock_server):
    imposter = Imposter(Stub(responses=Response(mode=Response.Mode.BINARY, body=b"c2F1c2FnZXM=")))

    with mock_server(imposter):
        response = httpx.get(str(imposter.url))

        assert_that(response, is_response().with_content(b"sausages"))


def test_multiple_responses(mock_server):
    imposter = Imposter(Stub(responses=[Response(body="sausages"), Response(body="egg")]))

    with mock_server(imposter):
        r1 = httpx.get(str(imposter.url))
        r2 = httpx.get(str(imposter.url))
        r3 = httpx.get(str(imposter.url))

        assert_that(r1, is_response().with_body("sausages"))
        assert_that(r2, is_response().with_body("egg"))
        assert_that(r3, is_response().with_body("sausages"))


@pytest.mark.skipif(
    Decimal(os.environ.get("MBTEST_VERSION", "2.0")) < 2,
    reason="Injection requires Mountebank version 2.0 or higher.",
)
def test_injection_response(mock_server):
    imposter = Imposter(
        Stub(
            responses=InjectionResponse(
                inject="function (config) {return {body: config.request.headers['foo'].toUpperCase()};}"
            )
        )
    )

    with mock_server(imposter):
        response = httpx.get(str(imposter.url), headers={"foo": "bar"})

        assert_that(response, is_response().with_body("BAR"))


@pytest.mark.skipif(
    Decimal(os.environ.get("MBTEST_VERSION", "2.6")) < Decimal("2.6"),
    reason="Fault responses require Mountebank version 2.6 or higher.",
)
def test_connection_reset_by_peer_response(mock_server):
    imposter = Imposter(Stub(responses=FaultResponse(FaultResponse.Fault.CONNECTION_RESET_BY_PEER)))

    with mock_server(imposter), pytest.raises(httpx.HTTPError, match="Server disconnected without sending a response"):
        httpx.get(str(imposter.url))


@pytest.mark.skipif(
    Decimal(os.environ.get("MBTEST_VERSION", "2.6")) < Decimal("2.6"),
    reason="Fault responses require Mountebank version 2.6 or higher.",
)
def test_random_data_then_close_response(mock_server):
    imposter = Imposter(Stub(responses=FaultResponse(FaultResponse.Fault.RANDOM_DATA_THEN_CLOSE)))

    with mock_server(imposter), pytest.raises(httpx.HTTPError, match="Server disconnected without sending a response"):
        httpx.get(str(imposter.url))


def test_json_body(mock_server):
    imposter = Imposter(Stub(responses=Response(body={"a": "b", "c": "d"})))

    with mock_server(imposter):
        response = httpx.get(str(imposter.url))

        assert_that(response, is_response().with_body(json_matching(has_entries(a="b", c="d"))))
