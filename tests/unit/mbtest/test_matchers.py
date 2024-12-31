import json
from unittest.mock import MagicMock

from brunns.matchers.matcher import mismatches_with
from hamcrest import all_of, assert_that, contains_string, has_entries, has_string, not_

from mbtest.matchers import email_sent, had_request
from tests.utils.builders import HttpRequestBuilder, SentEmailBuilder


def test_request_matcher():
    # Given
    server = MagicMock()
    request = HttpRequestBuilder().with_path("/test").and_method("GET").build()
    server.get_actual_requests.return_value = [request, request]

    # When

    # Then
    assert_that(server, had_request().with_path("/test").and_method("GET"))
    assert_that(server, had_request().with_times(2).and_path("/test").and_method("GET"))
    assert_that(server, not_(had_request().with_path("/somewhereelse").and_method("GET")))
    assert_that(
        had_request().with_path("/sausages").and_method("PUT"),
        has_string("call with method: 'PUT' path: '/sausages'"),
    )
    assert_that(
        had_request().with_times(4).and_query(has_entries(a="b")).and_body("chips"),
        has_string("<4> call(s) with query parameters: a dictionary containing {'a': 'b'} body: 'chips'"),
    )
    assert_that(
        had_request().with_path("/sausages").and_method("PUT").and_times(99),
        mismatches_with(
            server,
            all_of(
                contains_string(
                    "found <0> matching requests: <[]>. All requests: <[mbtest.imposters.imposters.HttpRequest"
                ),
                contains_string("path='/test'"),
                contains_string("method='GET'"),
            ),
        ),
    )


def test_request_matcher_with_json():
    # Given
    server = MagicMock()
    request1 = (
        HttpRequestBuilder().with_path("/test").and_method("GET").and_body(json.dumps({"a": "b", "c": "d"})).build()
    )
    request2 = (
        HttpRequestBuilder().with_path("/test").and_method("GET").and_body(json.dumps({"e": "f", "g": "j"})).build()
    )
    server.get_actual_requests.return_value = [request1, request2]

    # When

    # Then
    assert_that(
        server,
        had_request().with_times(1).and_json(has_entries(a="b")).and_method("GET"),
    )


def test_email_sent():
    # Given
    server = MagicMock()
    request = SentEmailBuilder().with_text("sausages").build()
    server.get_actual_requests.return_value = [request, request]

    # When

    # Then
    assert_that(server, email_sent(body_text="sausages"))
    assert_that(server, not_(email_sent(body_text="chips")))
    assert_that(email_sent(body_text="sausages"), has_string("email with body text: 'sausages'"))
    assert_that(
        email_sent(body_text="chips"),
        mismatches_with(
            server,
            all_of(
                contains_string("found <0> matching emails: <[]>. All emails: <["),
                contains_string("text='sausages'"),
            ),
        ),
    )
