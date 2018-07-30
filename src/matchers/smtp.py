import email
import re

from hamcrest import equal_to, anything
from hamcrest.core.base_matcher import BaseMatcher
from hamcrest.core.matcher import Matcher

ANYTHING = anything()


def email_with(to_name=ANYTHING, subject=ANYTHING, body_text=ANYTHING):
    """Match email with
    :param to_name:
    :type to_name: Matcher(str) or str
    :param subject:
    :type subject: Matcher(str) or str
    :param body_text:
    :type body_text: Matcher(str) or str
    :return: Matcher
    :rtype: Matcher(str)
    """
    return EmailWith(to_name, subject, body_text)


class EmailWith(BaseMatcher):
    def __init__(self, to_name=ANYTHING, subject=ANYTHING, body_text=ANYTHING):
        self.to_name = to_name if isinstance(to_name, Matcher) else equal_to(to_name)
        self.subject = subject if isinstance(subject, Matcher) else equal_to(subject)
        self.body_text = body_text if isinstance(body_text, Matcher) else equal_to(body_text)

    def _matches(self, actual_email):
        actual_to_name, actual_subject, actual_body_text = self._parse_email(actual_email)
        return (
            self.to_name.matches(actual_to_name)
            and self.subject.matches(actual_subject)
            and self.body_text.matches(actual_body_text)
        )

    def _parse_email(self, actual_email):
        parsed = email.message_from_string(actual_email)
        actual_to_name, actual_to_address = re.match("(.*) <(.*)>", parsed["To"]).groups()
        actual_subject = parsed["Subject"]
        actual_body_text = parsed.get_payload()
        return actual_to_name, actual_subject, actual_body_text

    def describe_to(self, description):
        description.append_text(
            "email with to_name {0} subject {1} body_text {2}".format(self.to_name, self.subject, self.body_text)
        )

    def describe_mismatch(self, actual_email, mismatch_description):
        actual_to_name, actual_subject, actual_body_text = self._parse_email(actual_email)
        mismatch_description.append_text("was to_name ").append_value(actual_to_name).append_text(
            " subject "
        ).append_value(actual_subject).append_text(" body_text ").append_value(actual_body_text)
