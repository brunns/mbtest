# encoding=utf-8
import logging

from brunns.matchers.object import has_identical_properties_to
from hamcrest import assert_that, instance_of

from mbtest.imposters.responses import (
    BaseResponse,
    HttpResponse,
    InjectionResponse,
    Response,
    TcpResponse,
)
from tests.utils.builders import (
    CopyBuilder,
    HttpResponseBuilder,
    InjectionResponseBuilder,
    LookupBuilder,
    ResponseBuilder,
    TcpResponseBuilder,
)

logger = logging.getLogger(__name__)


def test_structure_headers():
    expected_response = Response(headers={"X-Clacks-Overhead": "GNU Terry Pratchett"})
    response_structure = expected_response.as_structure()
    response = BaseResponse.from_structure(response_structure)
    assert response.headers == expected_response.headers


def test_structure_body():
    expected_response = Response(body="darwin")
    response_structure = expected_response.as_structure()
    response = BaseResponse.from_structure(response_structure)
    assert response.body == expected_response.body


def test_structure_status():
    expected_response = Response(status_code=204)
    response_structure = expected_response.as_structure()
    response = BaseResponse.from_structure(response_structure)
    assert response.status_code == expected_response.status_code


def test_structure_no_status():
    expected_response = Response()
    response_structure = expected_response.as_structure()
    del response_structure["is"]["statusCode"]
    response = BaseResponse.from_structure(response_structure)
    assert response.status_code == expected_response.status_code


def test_structure_repeat():
    expected_response = Response(repeat=1)
    response_structure = expected_response.as_structure()
    response = BaseResponse.from_structure(response_structure)
    assert response.repeat == expected_response.repeat


def test_structure_wait():
    expected_response = Response(wait=300)
    response_structure = expected_response.as_structure()
    response = BaseResponse.from_structure(response_structure)
    assert response.wait == expected_response.wait


def test_response_structure_roundtrip():
    # Given
    expected = ResponseBuilder(mode=None, copy=None, lookup=None).build()
    structure = expected.as_structure()

    # When
    actual = BaseResponse.from_structure(structure)

    # Then
    assert_that(actual, instance_of(Response))
    assert_that(actual, has_identical_properties_to(expected))


def test_response_with_copy_and_lookup_structure_roundtrip():
    # Given
    expected = ResponseBuilder(
        mode=Response.Mode.TEXT, copy=CopyBuilder().build(), lookup=LookupBuilder().build()
    ).build()
    structure = expected.as_structure()

    # When
    actual = BaseResponse.from_structure(structure)

    # Then
    assert_that(actual, instance_of(Response))
    assert_that(actual, has_identical_properties_to(expected))


def test_tcp_response_structure_roundtrip():
    # Given
    expected = TcpResponseBuilder().build()
    structure = expected.as_structure()

    # When
    actual = BaseResponse.from_structure(structure)

    # Then
    assert_that(actual, instance_of(TcpResponse))
    assert_that(actual, has_identical_properties_to(expected))


def test_injection_response_structure_roundtrip():
    # Given
    expected = InjectionResponseBuilder().build()
    structure = expected.as_structure()

    # When
    actual = BaseResponse.from_structure(structure)

    # Then
    assert_that(actual, instance_of(InjectionResponse))
    assert_that(actual, has_identical_properties_to(expected))


def test_http_response_roundtrip():
    # Given
    expected = HttpResponseBuilder().build()
    structure = expected.as_structure()

    # When
    actual = HttpResponse.from_structure(structure)

    # Then
    assert_that(actual, instance_of(HttpResponse))
    assert_that(actual, has_identical_properties_to(expected))
