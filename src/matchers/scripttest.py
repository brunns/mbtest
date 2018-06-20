from hamcrest.core.base_matcher import BaseMatcher


def found_file_containing(expected):
    """scripttest.FoundFile containing"""
    return FoundFileContaining(expected)


class FoundFileContaining(BaseMatcher):
    """scripttest.FoundFile containing"""

    def __init__(self, expected):
        self.expected = expected

    def _matches(self, found_file):
        return self.expected in found_file

    def describe_to(self, description):
        description.append_text("FoundFile containing ").append_value(self.expected)

    def describe_mismatch(self, found_file, mismatch_description):
        mismatch_description.append_text("got {}.").append_value(found_file)
