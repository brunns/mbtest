from hamcrest import contains_string, assert_that, has_string

from matchers.matcher import mismatches_with, matches, mismatches


def test_matcher_mismatches_with():
    # Given
    banana_matcher = contains_string("Banana")

    # When

    # Then
    assert_that(banana_matcher, matches("Banana"))
    assert_that(banana_matcher, mismatches("Apple"))
    assert_that(banana_matcher, mismatches_with("Apple", "was 'Apple'"))
    assert_that(banana_matcher, has_string("a string containing 'Banana'"))
