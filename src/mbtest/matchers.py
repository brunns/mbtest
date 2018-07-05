from hamcrest import anything, equal_to
from hamcrest.core.base_matcher import BaseMatcher
from hamcrest.core.core.isanything import IsAnything
from hamcrest.core.matcher import Matcher
from more_itertools import flatten

ANYTHING = anything()


def had_request(method=ANYTHING, path=ANYTHING, query=ANYTHING, headers=ANYTHING, body=ANYTHING, times=ANYTHING):
    """Mountebank server has recorded call matching"""
    return HadRequest(method=method, path=path, query=query, headers=headers, body=body, times=times)


class HadRequest(BaseMatcher):
    """Mountebank server has recorded call matching"""

    def __init__(self, method=ANYTHING, path=ANYTHING, query=ANYTHING, headers=ANYTHING, body=ANYTHING, times=ANYTHING):
        self.method = method if isinstance(method, Matcher) else equal_to(method)
        self.path = path if isinstance(path, Matcher) else equal_to(path)
        self.query = query if isinstance(query, Matcher) else equal_to(query)
        self.headers = headers if isinstance(headers, Matcher) else equal_to(headers)
        self.body = body if isinstance(body, Matcher) else equal_to(body)
        self.times = times if isinstance(times, Matcher) else equal_to(times)

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

    def _append_matcher_descrption(self, description, matcher, text):
        if not isinstance(matcher, IsAnything):
            description.append_text(" {0}: ".format(text)).append_description_of(matcher)

    def describe_mismatch(self, server, description):
        description.append_text("found ").append_description_of(len(self.matching_requests))
        description.append_text(" matching requests: ").append_description_of(self.matching_requests)
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
        self.body_text = body_text if isinstance(body_text, Matcher) else equal_to(body_text)
        self.subject = subject if isinstance(subject, Matcher) else equal_to(subject)
        self.to = to if isinstance(to, Matcher) else equal_to(to)

    def describe_to(self, description):
        description.append_text("email with")
        self._optional_description(description)

    def _optional_description(self, description):
        self._append_matcher_descrption(description, self.body_text, "body text")
        self._append_matcher_descrption(description, self.subject, "subject")
        self._append_matcher_descrption(description, self.to, "to")

    def _append_matcher_descrption(self, description, matcher, text):
        if not isinstance(matcher, IsAnything):
            description.append_text(" {0}: ".format(text)).append_description_of(matcher)

    def describe_mismatch(self, server, description):
        description.append_text("found ").append_description_of(len(self.matching_requests))
        description.append_text(" matching requests: ").append_description_of(self.matching_requests)
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
