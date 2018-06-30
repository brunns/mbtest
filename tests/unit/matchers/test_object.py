from hamcrest import assert_that, contains_string, has_string, not_, matches_regexp

from junkdrawer.bunch import Bunch
from matchers.matcher import mismatches_with
from matchers.object import has_repr, has_identical_properties_to, false, true


def test_has_repr():
    # Given
    r = [1, "2"]

    # When

    # Then
    assert_that(r, has_repr("[1, '2']"))
    assert_that(r, has_repr(contains_string("[1")))
    assert_that(has_repr("a"), has_string("an object with repr() matching 'a'"))
    assert_that(has_repr("a"), mismatches_with("b", "was 'b'"))


def test_identical_properties():
    # Given
    a = Bunch(a=1, b=2)
    b = Bunch(a=1, b=2)
    c = Bunch(a=1, b=3)

    # When

    # Then
    assert_that(a, has_identical_properties_to(b))
    assert_that(a, not_(has_identical_properties_to(c)))
    assert_that(
        has_identical_properties_to(a),
        has_string(matches_regexp(r"object with identical properties to object .*Bunch\(a=1, b=2\)")),
    )
    assert_that(has_identical_properties_to(a), mismatches_with(c, matches_regexp(r"was .*Bunch\(a=1, b=3\)")))


def test_truthy():
    assert_that([1], true())
    assert_that([], false())
    assert_that(true(), has_string("Truthy value"))
    assert_that(false(), has_string("not Truthy value"))
    assert_that(true(), mismatches_with([], "was <[]>"))
