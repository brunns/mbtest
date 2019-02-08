# encoding=utf-8
import logging

import requests
import pytest
from brunns.matchers.response import response_with
from hamcrest import assert_that, is_, has_entry

from mbtest.imposters import Imposter, Response, Stub

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


def test_structure_headers():
    expected_response = Response(headers={"X-Clacks-Overhead": "GNU Terry Pratchett"})
    response_structure = expected_response.as_structure()
    response = Response.from_structure(response_structure)
    assert response.headers == expected_response.headers


def test_structure_body():
    expected_response = Response(body="darwin")
    response_structure = expected_response.as_structure()
    response = Response.from_structure(response_structure)
    assert response.body == expected_response.body


def test_structure_status():
    expected_response = Response(status_code=204)
    response_structure = expected_response.as_structure()
    response = Response.from_structure(response_structure)
    assert response.status_code == expected_response.status_code


def test_structure_no_status():
    expected_response = Response()
    response_structure = expected_response.as_structure()
    del response_structure["is"]["statusCode"]
    response = Response.from_structure(response_structure)
    assert response.status_code == expected_response.status_code


def test_structure_repeat():
    expected_response = Response(repeat=1)
    response_structure = expected_response.as_structure()
    response = Response.from_structure(response_structure)
    assert response.repeat == expected_response.repeat


def test_structure_wait():
    expected_response = Response(wait=300)
    response_structure = expected_response.as_structure()
    response = Response.from_structure(response_structure)
    assert response.wait == expected_response.wait
