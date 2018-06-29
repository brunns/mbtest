from hamcrest import equal_to
from hamcrest.core.base_matcher import BaseMatcher
from hamcrest.core.matcher import Matcher


def has_response_code(code):
    return HasResponseCode(code)


class HasResponseCode(BaseMatcher):
    def __init__(self, code):
        super(HasResponseCode).__init__()
        self.code = code if isinstance(code, Matcher) else equal_to(code)

    def _matches(self, response):
        return response.status_code == self.code

    def describe_to(self, description):
        description.append_text("request has response code ").append_description_of(self.code)

    def describe_mismatch(self, response, mismatch_description):
        mismatch_description.append_text("was ").append_value(response)


def has_body_containing(matcher):
    return HasBodyContaining(matcher)


class HasBodyContaining(BaseMatcher):
    def __init__(self, matcher):
        super(HasBodyContaining).__init__()
        self.matcher = matcher if isinstance(matcher, Matcher) else equal_to(matcher)

    def _matches(self, response):
        return self.matcher.matches(self.decode_data(response))

    def describe_to(self, description):
        description.append_text("response containing body text ").append_description_of(self.matcher)

    def describe_mismatch(self, response, description):
        description.append_text("was ").append_value(response).append_text(" with body ").append_value(
            self.decode_data(response)
        ).append_text("\n")

        self.matcher.describe_mismatch(self.decode_data(response), description)

    @staticmethod
    def decode_data(response):
        return response.data.decode(response.charset)
