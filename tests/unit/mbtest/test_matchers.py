from hamcrest import assert_that, not_, has_string, contains_string, all_of
from mock import MagicMock

from matchers.matcher import mismatches_with
from mbtest.matchers import had_request, email_sent


def test_request_matcher():
    # Given
    server = MagicMock()
    request = dict(path="/test", method="GET")
    server.get_actual_requests.return_value = {"someport": [request, request]}

    # When

    # Then
    assert_that(server, had_request(path="/test", method="GET"))
    assert_that(server, had_request(path="/test", method="GET", times=2))
    assert_that(server, not_(had_request(path="/somewhereelse", method="GET")))
    assert_that(had_request(path="/sausages", method="PUT"), has_string("call with method: 'PUT' path: '/sausages'"))
    assert_that(had_request(path="/sausages", times=4), has_string("<4> call(s) with path: '/sausages'"))
    assert_that(
        had_request(path="/sausages", method="PUT"),
        mismatches_with(
            server,
            all_of(
                contains_string("found <0> matching requests: <[]>. All requests: <[{"),
                contains_string("'path': '/test'"),
                contains_string("'method': 'GET'"),
            ),
        ),
    )


def test_email_sent():
    # Given
    server = MagicMock()
    request = dict(envelopeFrom="", text="sausages")
    server.get_actual_requests.return_value = {"someport": [request, request]}

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
                contains_string("found <0> matching requests: <[]>. All requests: <[{"),
                contains_string("'text': 'sausages'"),
            ),
        ),
    )
