# encoding=utf-8
from hamcrest import anything
from hamcrest.core.base_matcher import BaseMatcher
from hamcrest.core.core.isanything import IsAnything
from hamcrest.core.helpers.wrap_matcher import wrap_matcher
from more_itertools import flatten

ANYTHING = anything()


def had_request(
    method=ANYTHING, path=ANYTHING, query=ANYTHING, headers=ANYTHING, body=ANYTHING, times=ANYTHING
):
    """Mountebank server has recorded call matching"""
    return HadRequest(
        method=method, path=path, query=query, headers=headers, body=body, times=times
    )


class HadRequest(BaseMatcher):
    """Mountebank server has recorded call matching"""

    def __init__(
        self,
        method=ANYTHING,
        path=ANYTHING,
        query=ANYTHING,
        headers=ANYTHING,
        body=ANYTHING,
        times=ANYTHING,
    ):
        self.method = wrap_matcher(method)
        self.path = wrap_matcher(path)
        self.query = wrap_matcher(query)
        self.headers = wrap_matcher(headers)
        self.body = wrap_matcher(body)
        self.times = wrap_matcher(times)

    def describe_to(self, description):
        if isinstance(self.times, IsAnything):
            description.append_text("call with")
        else:
            description.append_description_of(self.times).append_text(" call(s) with")

        self._optional_description(description)

    def _optional_description(self, description):
        self._append_matcher_descrption(description, self.method, "method")
        self._append_matcher_descrption(description, self.path, "path")
        self._append_matcher_descrption(description, self.query, "query parameters")
        self._append_matcher_descrption(description, self.headers, "headers")
        self._append_matcher_descrption(description, self.body, "body")

    @staticmethod
    def _append_matcher_descrption(description, matcher, text):
        if not isinstance(matcher, IsAnything):
            description.append_text(" {0}: ".format(text)).append_description_of(matcher)

    def describe_mismatch(self, server, description):
        description.append_text("found ").append_description_of(len(self.matching_requests))
        description.append_text(" matching requests: ").append_description_of(
            self.matching_requests
        )
        description.append_text(". All requests: ").append_description_of(self.all_requests)

    def _matches(self, server):
        self.all_requests = list(flatten(server.get_actual_requests().values()))
        self.matching_requests = [
            request
            for request in self.all_requests
            if self.method.matches(request.get("method", None))
            and self.path.matches(request.get("path", None))
            and self.query.matches(request.get("query", None))
            and self.headers.matches(request.get("headers", None))
            and self.body.matches(request.get("body", None))
        ]

        if isinstance(self.times, IsAnything):
            return len(self.matching_requests) > 0

        return self.times.matches(len(self.matching_requests))


def email_sent(to=ANYTHING, subject=ANYTHING, body_text=ANYTHING):
    return EmailSent(to, subject, body_text)


class EmailSent(BaseMatcher):
    def __init__(self, to=ANYTHING, subject=ANYTHING, body_text=ANYTHING):
        self.body_text = wrap_matcher(body_text)
        self.subject = wrap_matcher(subject)
        self.to = wrap_matcher(to)

    def describe_to(self, description):
        description.append_text("email with")
        self._optional_description(description)

    def _optional_description(self, description):
        self._append_matcher_descrption(description, self.body_text, "body text")
        self._append_matcher_descrption(description, self.subject, "subject")
        self._append_matcher_descrption(description, self.to, "to")

    @staticmethod
    def _append_matcher_descrption(description, matcher, text):
        if not isinstance(matcher, IsAnything):
            description.append_text(" {0}: ".format(text)).append_description_of(matcher)

    def describe_mismatch(self, server, description):
        description.append_text("found ").append_description_of(len(self.matching_requests))
        description.append_text(" matching requests: ").append_description_of(
            self.matching_requests
        )
        description.append_text(". All requests: ").append_description_of(self.all_requests)

    def _matches(self, server):
        self.all_requests = list(flatten(server.get_actual_requests().values()))
        self.matching_requests = [
            request
            for request in self.all_requests
            if "envelopeFrom" in request
            and self.body_text.matches(request.get("text", None))
            and self.subject.matches(request.get("subject", None))
            and self.to.matches(request.get("to", None))
        ]

        return len(self.matching_requests) > 0
