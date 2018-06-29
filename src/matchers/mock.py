from hamcrest import equal_to
from hamcrest.core.base_matcher import BaseMatcher
from hamcrest.core.matcher import Matcher
from six.moves import zip_longest


def call_has_arg(index, expected):
    return CallHasArg(index, expected)


class CallHasArg(BaseMatcher):
    def __init__(self, index, expected):
        super(CallHasArg, self).__init__()
        self.index = index
        self.expected = expected if isinstance(expected, Matcher) else equal_to(expected)

    def _matches(self, actual_call):
        return self.expected.matches(actual_call[1][self.index])

    def describe_to(self, description):
        description.append_text("mock.call with positional argument {} matching {}.".format(self.index, self.expected))

    def describe_mismatch(self, actual_call, mismatch_description):
        mismatch_description.append_text("got  {} {}.".format(actual_call.call_args[0], actual_call.call_args[1]))


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
        description.append_text("mock instance has mock.call matching ").append_description_of(self.call_matcher)

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
        description.append_text("mock.call with arguments (")
        for arg in self.args:
            description.append_description_of(arg).append_text(' ,"')
        description.append_text(") {")
        for key, value in self.kwargs.items():
            description.append_value(key).append_text(": ").append_description_of(value).append_text(' ,"')
        description.append_text("}")

    def describe_mismatch(self, actual_call, mismatch_description):
        if actual_call.call_args:
            mismatch_description.append_text(
                "got arguments {} {}".format(actual_call.call_args[0], actual_call.call_args[1])
            )
        else:
            mismatch_description.append_text("not called")
