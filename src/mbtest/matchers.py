# encoding=utf-8
from typing import Any, Mapping, Union

from furl import furl
from hamcrest import anything
from hamcrest.core.base_matcher import BaseMatcher
from hamcrest.core.core.isanything import IsAnything
from hamcrest.core.description import Description
from hamcrest.core.helpers.wrap_matcher import wrap_matcher
from hamcrest.core.matcher import Matcher
from mbtest.server import MountebankServer
from more_itertools import flatten

ANYTHING = anything()


def had_request(
    method: Union[str, Matcher[str]] = ANYTHING,
    path: Union[furl, str, Matcher[Union[furl, str]]] = ANYTHING,
    query: Union[Mapping[str, str], Matcher[Mapping[str, str]]] = ANYTHING,
    headers: Union[Mapping[str, str], Matcher[Mapping[str, str]]] = ANYTHING,
    body: Union[str, Matcher[str]] = ANYTHING,
    times: Union[int, Matcher[int]] = ANYTHING,
) -> Matcher[MountebankServer]:
    """Mountebank server has recorded call matching.

    Build criteria with `with_` and `and_` methods:

        assert_that(server, had_request().with_path("/test").and_method("GET"))

    Available attributes as per parameters.

    :param method: Request's method matched...
    :param path: Request's path matched...
    :param query: Request's query matched...
    :param headers: Request's headers matched...
    :param body: Request's body matched...
    :param times: Request's number of times called matched matched...
    """
    return HadRequest(
        method=method, path=path, query=query, headers=headers, body=body, times=times
    )


class HadRequest(BaseMatcher):
    """Mountebank server has recorded call matching

    :param method: Request's method matched...
    :param path: Request's path matched...
    :param query: Request's query matched...
    :param headers: Request's headers matched...
    :param body: Request's body matched...
    :param times: Request's number of times called matched matched...
    """

    def __init__(
        self,
        method: Union[str, Matcher[str]] = ANYTHING,
        path: Union[furl, str, Matcher[Union[furl, str]]] = ANYTHING,
        query: Union[Mapping[str, str], Matcher[Mapping[str, str]]] = ANYTHING,
        headers: Union[Mapping[str, str], Matcher[Mapping[str, str]]] = ANYTHING,
        body: Union[str, Matcher[str]] = ANYTHING,
        times: Union[int, Matcher[int]] = ANYTHING,
    ):
        self.method = wrap_matcher(method)  # type: Matcher[str]
        self.path = wrap_matcher(path)  # type: Matcher[Union[furl, str]]
        self.query = wrap_matcher(query)  # type Matcher[Mapping[str, str]]
        self.headers = wrap_matcher(headers)  # type Matcher[Mapping[str, str]]
        self.body = wrap_matcher(body)  # type: Matcher[str]
        self.times = wrap_matcher(times)  # type: Matcher[int]

    def describe_to(self, description: Description) -> None:
        if isinstance(self.times, IsAnything):
            description.append_text("call with")
        else:
            description.append_description_of(self.times).append_text(" call(s) with")

        self._optional_description(description)

    def _optional_description(self, description: Description) -> None:
        self.append_matcher_description(self.method, "method", description)
        self.append_matcher_description(self.path, "path", description)
        self.append_matcher_description(self.query, "query parameters", description)
        self.append_matcher_description(self.headers, "headers", description)
        self.append_matcher_description(self.body, "body", description)

    @staticmethod
    def append_matcher_description(
        field_matcher: Matcher[Any], field_name: str, description: Description
    ) -> None:
        if not isinstance(field_matcher, IsAnything):
            description.append_text(" {0}: ".format(field_name)).append_description_of(
                field_matcher
            )

    def describe_mismatch(self, server: MountebankServer, description: Description) -> None:
        description.append_text("found ").append_description_of(len(self.matching_requests))
        description.append_text(" matching requests: ").append_description_of(
            self.matching_requests
        )
        description.append_text(". All requests: ").append_description_of(self.all_requests)

    def _matches(self, server: MountebankServer) -> bool:
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

    def with_method(self, method: Union[str, Matcher[str]]):
        self.method = wrap_matcher(method)
        return self

    def and_method(self, method: Union[str, Matcher[str]]):
        return self.with_method(method)

    def with_path(self, path: Union[furl, str, Matcher[Union[furl, str]]]):
        self.path = wrap_matcher(path)
        return self

    def and_path(self, path: Union[furl, str, Matcher[Union[furl, str]]]):
        return self.with_path(path)

    def with_query(self, query: Union[Mapping[str, str], Matcher[Mapping[str, str]]]):
        self.query = wrap_matcher(query)
        return self

    def and_query(self, query: Union[Mapping[str, str], Matcher[Mapping[str, str]]]):
        return self.with_query(query)

    def with_headers(self, headers: Union[Mapping[str, str], Matcher[Mapping[str, str]]]):
        self.headers = wrap_matcher(headers)
        return self

    def and_headers(self, headers: Union[Mapping[str, str], Matcher[Mapping[str, str]]]):
        return self.with_headers(headers)

    def with_body(self, body: Union[str, Matcher[str]]):
        self.body = wrap_matcher(body)
        return self

    def and_body(self, body: Union[str, Matcher[str]]):
        return self.with_body(body)

    def with_times(self, times: Union[int, Matcher[int]]):
        self.times = wrap_matcher(times)
        return self

    def and_times(self, times: Union[int, Matcher[int]]):
        return self.with_times(times)


def email_sent(
    to: Union[str, Matcher[str]] = ANYTHING,
    subject: Union[str, Matcher[str]] = ANYTHING,
    body_text: Union[str, Matcher[str]] = ANYTHING,
) -> Matcher[MountebankServer]:
    """Mountebank SMTP server was asked to sent email matching:

    :param to: Email's to field matched...
    :param subject: Email's subject field matched...
    :param body_text: Email's body matched...
    """
    return EmailSent(to, subject, body_text)


class EmailSent(BaseMatcher):
    """Mountebank SMTP server was asked to sent email matching:

    :param to: Email's to field matched...
    :param subject: Email's subject field matched...
    :param body_text: Email's body matched...
    """

    def __init__(
        self,
        to: Union[str, Matcher[str]] = ANYTHING,
        subject: Union[str, Matcher[str]] = ANYTHING,
        body_text: Union[str, Matcher[str]] = ANYTHING,
    ) -> None:
        self.body_text = wrap_matcher(body_text)
        self.subject = wrap_matcher(subject)
        self.to = wrap_matcher(to)

    def describe_to(self, description: Description) -> None:
        description.append_text("email with")
        self._optional_description(description)

    def _optional_description(self, description: Description) -> None:
        self._append_matcher_description(description, self.body_text, "body text")
        self._append_matcher_description(description, self.subject, "subject")
        self._append_matcher_description(description, self.to, "to")

    @staticmethod
    def _append_matcher_description(description: Description, matcher: Matcher, text: str) -> None:
        if not isinstance(matcher, IsAnything):
            description.append_text(" {0}: ".format(text)).append_description_of(matcher)

    def describe_mismatch(self, server: MountebankServer, description: Description) -> None:
        description.append_text("found ").append_description_of(len(self.matching_requests))
        description.append_text(" matching requests: ").append_description_of(
            self.matching_requests
        )
        description.append_text(". All requests: ").append_description_of(self.all_requests)

    def _matches(self, server: MountebankServer) -> bool:
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
