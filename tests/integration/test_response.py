# encoding=utf-8
import logging
import os
from decimal import Decimal

import pytest
import requests
from brunns.matchers.response import is_response
from hamcrest import assert_that, has_entry
from mbtest.imposters import Imposter, Response, Stub
from mbtest.imposters.responses import InjectionResponse

logger = logging.getLogger(__name__)


def test_body(mock_server):
    imposter = Imposter(Stub(responses=Response(body="sausages")), port=4545)

    with mock_server(imposter):
        response = requests.get(imposter.url)

        assert_that(response, is_response().with_body("sausages"))


def test_status(mock_server):
    imposter = Imposter(Stub(responses=Response(status_code=204)), port=4545)

    with mock_server(imposter):
        response = requests.get(imposter.url)

        assert_that(response, is_response().with_status_code(204))


def test_headers(mock_server):
    imposter = Imposter(
        Stub(responses=Response(headers={"X-Clacks-Overhead": "GNU Terry Pratchett"})), port=4545
    )

    with mock_server(imposter):
        response = requests.get(imposter.url)

        assert_that(
            response,
            is_response().with_headers(has_entry("X-Clacks-Overhead", "GNU Terry Pratchett")),
        )


def test_binary_mode(mock_server):
    imposter = Imposter(
        Stub(responses=Response(mode=Response.Mode.BINARY, body=b"c2F1c2FnZXM=")), port=4545
    )

    with mock_server(imposter):
        response = requests.get(imposter.url)

        assert_that(response, is_response().with_content(b"sausages"))


def test_multiple_responses(mock_server):
    imposter = Imposter(
        Stub(responses=[Response(body="sausages"), Response(body="egg")]), port=4545
    )

    with mock_server(imposter):
        r1 = requests.get(imposter.url)
        r2 = requests.get(imposter.url)
        r3 = requests.get(imposter.url)

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
        ),
        port=4545,
    )

    with mock_server(imposter):
        response = requests.get(imposter.url, headers={"foo": "bar"})

        assert_that(response, is_response().with_body("BAR"))
