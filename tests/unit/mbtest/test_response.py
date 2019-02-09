# encoding=utf-8
import logging

from mbtest.imposters import Response

logger = logging.getLogger(__name__)


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
