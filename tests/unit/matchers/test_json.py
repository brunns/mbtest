import json

from hamcrest import assert_that, contains, has_string

from matchers.data import json_matching
from matchers.matcher import mismatches_with


def test_json_matching():
    # Given
    j = json.dumps([1, 2, 3])

    # When

    # Then
    assert_that(j, json_matching([1, 2, 3]))
    assert_that(j, json_matching(contains(1, 2, 3)))
    assert_that(json_matching([1]), has_string("JSON structure matching <[1]>"))
    assert_that(json_matching([]), mismatches_with("WTF?", "Got invalid JSON 'WTF?'"))
    assert_that(json_matching([]), mismatches_with("[1]", "was <[1]>"))
