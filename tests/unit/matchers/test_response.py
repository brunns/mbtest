from hamcrest import assert_that, has_string, not_
from mock import MagicMock

from matchers.matcher import mismatches_with
from matchers.response import response_with


def test_response_matcher():
    # Given
    response = MagicMock(status_code=200, text="sausages", headers={})

    # When

    # Then
    assert_that(response, response_with(status_code=200, body="sausages"))
    assert_that(response, not_(response_with(status_code=200, body="chips")))
    assert_that(
        response_with(status_code=200, body="chips"), has_string("response with status_code: <200> body: 'chips'")
    )
    assert_that(
        response_with(status_code=200, body="chips"),
        mismatches_with(response, "was response with status code: <200> body: 'sausages' headers: <{}>"),
    )
