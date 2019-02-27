# encoding=utf-8
from __future__ import unicode_literals, absolute_import, division, print_function

import logging

import requests
from brunns.matchers.response import response_with
from hamcrest import assert_that, is_, has_entry

from mbtest.imposters import Imposter, Response, Stub, Copy, UsingRegex

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
    imposter = Imposter(Stub(responses=Response(headers={"X-Clacks-Overhead": "GNU Terry Pratchett"})))

    with mock_server(imposter):
        response = requests.get(imposter.url)

        assert_that(response, is_(response_with(headers=has_entry("X-Clacks-Overhead", "GNU Terry Pratchett"))))


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


def test_regex_copy(mock_server):
    imposter = Imposter(
        Stub(
            responses=Response(
                status_code="${code}",
                headers={"X-Test": "${header}"},
                body="Hello, ${name}!",
                copy=[
                    Copy("path", "${code}", UsingRegex("\\d+")),
                    Copy({"headers": "X-Request"}, "${header}", UsingRegex(".+")),
                    Copy({"query": "name"}, "${name}", UsingRegex("AL\\w+", ignore_case=True)),
                ],
            )
        )
    )

    with mock_server(imposter):
        response = requests.get(
            '{imposter_url}/456'.format(imposter_url=imposter.url), params={"name": "Alice"}, headers={"X-REQUEST": "Header value"}
        )

        assert_that(
            response,
            is_(
                response_with(
                    status_code=456,
                    body="Hello, Alice!",
                    headers=has_entry("X-Test", "Header value"),
                )
            ),
        )
