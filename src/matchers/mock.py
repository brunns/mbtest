from itertools import chain
from numbers import Number

from hamcrest import equal_to
from hamcrest.core.base_matcher import BaseMatcher
from hamcrest.core.matcher import Matcher
from six.moves import zip_longest


def call_has_arg(arg, expected):
    if isinstance(arg, Number):
        return CallHasPositionalArg(arg, expected)
    else:
        return CallHasKeywordArg(arg, expected)


class CallHasPositionalArg(BaseMatcher):
    def __init__(self, index, expected):
        super(CallHasPositionalArg, self).__init__()
        self.index = index
        self.expected = expected if isinstance(expected, Matcher) else equal_to(expected)

    def _matches(self, actual_call):
        args = actual_call[1]
        return len(args) > self.index and self.expected.matches(args[self.index])

    def describe_to(self, description):
        description.append_text("mock.call with argument index ").append_description_of(self.index).append_text(
            " matching "
        )
        self.expected.describe_to(description)

    def describe_mismatch(self, actual_call, mismatch_description):
        args = actual_call[1]
        if len(args) > self.index:
            mismatch_description.append_text("got mock.call with argument index ").append_description_of(
                self.index
            ).append_text(" with value ").append_description_of(args[self.index])
        else:
            mismatch_description.append_text("got mock.call with without argument index ").append_description_of(
                self.index
            )


class CallHasKeywordArg(BaseMatcher):
    def __init__(self, key, expected):
        super(CallHasKeywordArg, self).__init__()
        self.key = key
        self.expected = expected if isinstance(expected, Matcher) else equal_to(expected)

    def _matches(self, actual_call):
        args = actual_call[2]
        return self.key in args and self.expected.matches(args[self.key])

    def describe_to(self, description):
        description.append_text("mock.call with keyword argument ").append_description_of(self.key).append_text(
            " matching "
        )
        self.expected.describe_to(description)

    def describe_mismatch(self, actual_call, mismatch_description):
        args = actual_call[2]
        if self.key in args:
            mismatch_description.append_text("got mock.call with keyword argument ").append_description_of(
                self.key
            ).append_text(" with value ").append_description_of(args[self.key])
        else:
            mismatch_description.append_text("got mock.call with without keyword argument ").append_description_of(
                self.key
            )


def has_call(call_matcher):
    return HasCall(call_matcher)


class HasCall(BaseMatcher):
    def __init__(self, call_matcher):
        super(HasCall, self).__init__()
        self.call_matcher = call_matcher

    def _matches(self, mock):
        for call in mock.mock_calls:
            if self.call_matcher.matches(call):
                return True
        return False

    def describe_to(self, description):
        description.append_text("has call matching ")
        self.call_matcher.describe_to(description)

    def describe_mismatch(self, mock, mismatch_description):
        mismatch_description.append_list("got calls [", ", ", "]", [str(c) for c in mock.mock_calls])


def call_has_args(*args, **kwargs):
    """mock.call with arguments"""
    return CallHasArgs(*args, **kwargs)


class CallHasArgs(BaseMatcher):
    """mock.call with arguments"""

    def __init__(self, *args, **kwargs):
        super(CallHasArgs, self).__init__()
        self.args = [arg if isinstance(arg, Matcher) else equal_to(arg) for arg in args]
        self.kwargs = {key: value if isinstance(value, Matcher) else equal_to(value) for key, value in kwargs.items()}

    def _matches(self, actual_call):
        actual_positional = actual_call[1]
        actual_keyword = actual_call[2]
        return all(m.matches(a) for m, a in zip_longest(self.args, actual_positional) if m is not None) and all(
            m.matches(actual_keyword.get(k, None)) for k, m in self.kwargs.items()
        )

    def describe_to(self, description):
        description.append_text("mock.call with arguments (").append_text(
            ", ".join(chain((str(a) for a in self.args), ("{0}={1}".format(k, v) for k, v in self.kwargs.items())))
        ).append_text(")")

    def describe_mismatch(self, call, mismatch_description):
        mismatch_description.append_text("got arguments (").append_text(
            ", ".join(chain((repr(a) for a in call[1]), ("{0}={1!r}".format(k, v) for k, v in call[2].items())))
        ).append_text(")")
