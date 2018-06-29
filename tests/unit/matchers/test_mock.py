from hamcrest import assert_that, contains_string, has_string, not_
from mock import MagicMock

from matchers.matcher import mismatches_with
from matchers.mock import call_has_arg


def test_call_has_arg():
    # Given
    m = MagicMock()

    # When
    m("first", "second", "third")
    call = m.mock_calls[0]

    # Then
    assert_that(call, call_has_arg(1, "second"))
    assert_that(call, call_has_arg(2, "third"))
    assert_that(call, not_(call_has_arg(4, "nope")))
    assert_that(call, call_has_arg(1, contains_string("eco")))
    assert_that(
        call_has_arg(1, contains_string("eco")),
        has_string("mock.call with positional argument index <1> matching a string containing 'eco'"),
    )
    assert_that(
        call_has_arg(1, "fifth"),
        mismatches_with(call, "got mock.call with positional argument index <1> with value 'second'"),
    )
    assert_that(
        call_has_arg(4, "nope"), mismatches_with(call, "got mock.call with without positional argument index <4>")
    )
