from hamcrest import equal_to, not_
from hamcrest.core.base_matcher import BaseMatcher
from hamcrest.core.matcher import Matcher


def has_repr(expected):
    """object with repr() matching"""
    return HasRepr(expected)


class HasRepr(BaseMatcher):
    """object with repr() matching"""

    def __init__(self, expected):
        self.expected = expected if isinstance(expected, Matcher) else equal_to(expected)

    def _matches(self, actual):
        return self.expected.matches(repr(actual))

    def describe_to(self, description):
        description.append_text("an object with repr() matching ")
        self.expected.describe_to(description)


def has_identical_properties_to(expected):
    return HasIdenticalPropertiesTo(expected)


class HasIdenticalPropertiesTo(BaseMatcher):
    def __init__(self, expected):
        self.expected = expected

    def _matches(self, actual):
        return actual.__dict__ == self.expected.__dict__

    def describe_to(self, description):
        description.append_text("object with identical properties to object ").append_description_of(self.expected)


class Truthy(BaseMatcher):
    def describe_to(self, description):
        description.append_text("Truthy value")

    def _matches(self, item):
        return bool(item)


def true():
    return Truthy()


def false():
    return not_(true())
