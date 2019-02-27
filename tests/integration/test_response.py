# encoding=utf-8
import logging

import requests
from brunns.matchers.response import response_with
from hamcrest import assert_that, is_, has_entry

from mbtest.imposters import Imposter, Response, Stub, Copy, Using

logger = logging.getLogger(__name__)


def test_body(mock_server):
    imposter = Imposter(Stub(responses=Response(body="sausages")))

    with mock_server(imposter):
        response = requests.get(imposter.url)

        assert_that(response, is_(response_with(body="sausages")))


def test_status(mock_server):
    imposter = Imposter(Stub(responses=Response(status_code=204)))

    with mock_server(imposter):
        response = requests.get(imposter.url)

        assert_that(response, is_(response_with(status_code=204)))


def test_headers(mock_server):
    imposter = Imposter(
        Stub(responses=Response(headers={"X-Clacks-Overhead": "GNU Terry Pratchett"}))
    )

    with mock_server(imposter):
        response = requests.get(imposter.url)

        assert_that(
            response,
            is_(response_with(headers=has_entry("X-Clacks-Overhead", "GNU Terry Pratchett"))),
        )


def test_binary_mode(mock_server):
    imposter = Imposter(Stub(responses=Response(mode=Response.Mode.BINARY, body=b"c2F1c2FnZXM=")))

    with mock_server(imposter):
        response = requests.get(imposter.url)

        assert_that(response, is_(response_with(content=b"sausages")))


def test_multiple_responses(mock_server):
    imposter = Imposter(Stub(responses=[Response(body="sausages"), Response(body="egg")]))

    with mock_server(imposter):
        r1 = requests.get(imposter.url)
        r2 = requests.get(imposter.url)
        r3 = requests.get(imposter.url)

        assert_that(r1, is_(response_with(body="sausages")))
        assert_that(r2, is_(response_with(body="egg")))
        assert_that(r3, is_(response_with(body="sausages")))


def test_copy(mock_server):
    imposter = Imposter(
        Stub(
            responses=Response(
                status_code="${code}",
                copy=Copy("path", "${code}", Using(Using.Method.REGEX, "\\d+")),
            )
        )
    )

    with mock_server(imposter):
        response = requests.get(imposter.url / str(456))

        assert_that(response, is_(response_with(status_code=456)))
