import json

from hamcrest import equal_to
from hamcrest.core.base_matcher import BaseMatcher
from hamcrest.core.matcher import Matcher


def json_matching(matcher):
    """Matches string containing JSON data.
    :param matcher: Expected JSON
    :type matcher: Matcher or dict or list
    :return: Matcher(str)
    """
    return JsonMatching(matcher)


class JsonMatching(BaseMatcher):
    def __init__(self, matcher):
        self.matcher = matcher if isinstance(matcher, Matcher) else equal_to(matcher)

    def describe_to(self, description):
        description.append_text("JSON structure matching ").append_description_of(self.matcher)

    def _matches(self, json_string):
        try:
            loads = json.loads(json_string)
        except ValueError:
            return False
        return self.matcher.matches(loads)

    def describe_mismatch(self, json_string, description):
        try:
            loads = json.loads(json_string)
        except ValueError:
            description.append_text("Got invalid JSON ").append_value(json_string)
        else:
            self.matcher.describe_mismatch(loads, description)
