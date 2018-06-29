from hamcrest import equal_to, anything, not_
from hamcrest.core.base_matcher import BaseMatcher
from hamcrest.core.matcher import Matcher
from hamcrest.core.string_description import StringDescription


def mismatches_with(value_not_to_match, expected_message):
    return MismatchesWith(value_not_to_match, expected_message)


def mismatches(value_not_to_match):
    return MismatchesWith(value_not_to_match, anything())


def matches(value_to_match):
    return not_(mismatches(value_to_match))


class MismatchesWith(BaseMatcher):
    def __init__(self, value_not_to_match, expected_message):
        super(MismatchesWith, self).__init__()
        self.value_not_to_match = value_not_to_match
        self.expected_message = (
            expected_message if isinstance(expected_message, Matcher) else equal_to(expected_message)
        )

    def _matches(self, matcher_under_test):
        desc = StringDescription()
        matches = matcher_under_test.matches(self.value_not_to_match, desc)
        return not matches and self.expected_message.matches(desc.out)

    def describe_to(self, description):
        description.append_text("a matcher which mismatches the value ").append_description_of(
            self.value_not_to_match
        ).append_text(" giving message ").append_description_of(self.expected_message)

    def describe_mismatch(self, matcher_under_test, description):
        desc = StringDescription()
        if matcher_under_test.matches(self.value_not_to_match, desc):
            description.append_text("matched")
            return
        description.append_text("got message ").append_description_of(desc)
