import logging
from http import HTTPStatus

from brunns.matchers.object import has_identical_properties_to
from hamcrest import assert_that, instance_of

from mbtest.imposters.responses import (
    BaseResponse,
    FaultResponse,
    HttpResponse,
    InjectionResponse,
    Response,
    TcpResponse,
)
from tests.utils.builders import (
    CopyFactory,
    FaultResponseFactory,
    HttpResponseFactory,
    InjectionResponseFactory,
    LookupFactory,
    ResponseFactory,
    TcpResponseFactory,
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
    expected_response = Response(status_code=HTTPStatus.NO_CONTENT)
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
    expected = ResponseFactory.build(copy=None, lookup=None)
    structure = expected.as_structure()

    # When
    actual = BaseResponse.from_structure(structure)

    # Then
    assert_that(actual, instance_of(Response))
    assert_that(actual, has_identical_properties_to(expected))


def test_response_with_copy_and_lookup_structure_roundtrip():
    # Given
    expected = ResponseFactory.build(copy=CopyFactory.build(), lookup=LookupFactory.build())
    structure = expected.as_structure()

    # When
    actual = BaseResponse.from_structure(structure)

    # Then
    assert_that(actual, instance_of(Response))
    assert_that(actual, has_identical_properties_to(expected))


def test_tcp_response_structure_roundtrip():
    # Given
    expected = TcpResponseFactory.build()
    structure = expected.as_structure()

    # When
    actual = BaseResponse.from_structure(structure)

    # Then
    assert_that(actual, instance_of(TcpResponse))
    assert_that(actual, has_identical_properties_to(expected))


def test_injection_response_structure_roundtrip():
    # Given
    expected = InjectionResponseFactory.build()
    structure = expected.as_structure()

    # When
    actual = BaseResponse.from_structure(structure)

    # Then
    assert_that(actual, instance_of(InjectionResponse))
    assert_that(actual, has_identical_properties_to(expected))


def test_http_response_roundtrip():
    # Given
    expected = HttpResponseFactory.build()
    structure = expected.as_structure()

    # When
    actual = HttpResponse.from_structure(structure)

    # Then
    assert_that(actual, instance_of(HttpResponse))
    assert_that(actual, has_identical_properties_to(expected))


def test_fault_response_roundtrip():
    # Given
    expected = FaultResponseFactory.build()
    structure = expected.as_structure()

    # When
    actual = BaseResponse.from_structure(structure)

    # Then
    assert_that(actual, instance_of(FaultResponse))
    assert_that(actual, has_identical_properties_to(expected))


def test_response_from_structure_without_behaviors():
    # Mountebank omits _behaviors when no behaviors are set on a live imposter
    # Given
    expected = ResponseFactory.build(
        copy=None, lookup=None, decorate=None, shell_transform=None, wait=None, repeat=None
    )
    structure = expected.as_structure()
    del structure["_behaviors"]

    # When
    actual = BaseResponse.from_structure(structure)

    # Then
    assert_that(actual, instance_of(Response))
    assert_that(actual, has_identical_properties_to(expected))


def test_http_response_structure_no_mode():
    expected_response = HttpResponse()
    response_structure = expected_response.as_structure()
    del response_structure["_mode"]
    response = HttpResponse.from_structure(response_structure)
    assert response.mode == Response.Mode.TEXT
