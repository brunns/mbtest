# encoding=utf-8
import warnings
from typing import Any, Mapping, Sequence, Union, cast

from furl import furl
from hamcrest import anything
from hamcrest.core.base_matcher import BaseMatcher
from hamcrest.core.core.isanything import IsAnything
from hamcrest.core.description import Description
from hamcrest.core.helpers.wrap_matcher import wrap_matcher
from hamcrest.core.matcher import Matcher
from imurl.url import URL

from mbtest.imposters.base import JsonStructure
from mbtest.imposters.imposters import HttpRequest, Imposter, SentEmail
from mbtest.server import MountebankServer

ANYTHING = anything()


def had_request(
    method: Union[str, Matcher[str]] = ANYTHING,
    path: Union[furl, str, Matcher[Union[furl, URL, str]]] = ANYTHING,
    query: Union[Mapping[str, str], Matcher[Mapping[str, str]]] = ANYTHING,
    headers: Union[Mapping[str, str], Matcher[Mapping[str, str]]] = ANYTHING,
    body: Union[str, Matcher[str]] = ANYTHING,
    times: Union[int, Matcher[int]] = ANYTHING,
) -> Matcher[Union[Imposter, MountebankServer]]:
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
        path: Union[furl, str, Matcher[Union[furl, URL, str]]] = ANYTHING,
        query: Union[Mapping[str, str], Matcher[Mapping[str, str]]] = ANYTHING,
        headers: Union[Mapping[str, str], Matcher[Mapping[str, str]]] = ANYTHING,
        body: Union[str, Matcher[str]] = ANYTHING,
        times: Union[int, Matcher[int]] = ANYTHING,
    ):
        if (
            method != ANYTHING
            or path != ANYTHING
            or query != ANYTHING
            or headers != ANYTHING
            or body != ANYTHING
            or times != ANYTHING
        ):  # pragma: no cover
            warnings.warn("Use builder-style with_X and and_X methods, rather than arguments.")
        self.method: Matcher[str] = wrap_matcher(method)
        self.path: Matcher[Union[furl, URL, str]] = wrap_matcher(path)
        self.query: Matcher[Mapping[str, str]] = wrap_matcher(query)
        self.headers: Matcher[Mapping[str, str]] = wrap_matcher(headers)
        self.body: Matcher[str] = wrap_matcher(body)
        self.json: Matcher[JsonStructure] = ANYTHING
        self.times: Matcher[int] = wrap_matcher(times)

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
        self.append_matcher_description(self.json, "json", description)

    @staticmethod
    def append_matcher_description(
        field_matcher: Matcher[Any], field_name: str, description: Description
    ) -> None:
        if not isinstance(field_matcher, IsAnything):
            description.append_text(f" {field_name}: ").append_description_of(field_matcher)

    def describe_mismatch(
        self, actual: Union[Imposter, MountebankServer], description: Description
    ) -> None:
        description.append_text("found ").append_description_of(len(self.matching_requests))
        description.append_text(" matching requests: ").append_description_of(
            self.matching_requests
        )
        description.append_text(". All requests: ").append_description_of(self.all_requests)

    def _matches(self, actual: Union[Imposter, MountebankServer]) -> bool:
        self.all_requests = cast(Sequence[HttpRequest], actual.get_actual_requests())
        self.matching_requests = [
            request
            for request in self.all_requests
            if self.method.matches(request.method)
            and self.path.matches(request.path)
            and self.query.matches(request.query)
            and self.headers.matches(request.headers)
            and self.body.matches(request.body)
            and self.json.matches(request.json)
        ]

        if isinstance(self.times, IsAnything):
            return len(self.matching_requests) > 0

        return self.times.matches(len(self.matching_requests))

    def with_method(self, method: Union[str, Matcher[str]]):
        self.method = wrap_matcher(method)
        return self

    def and_method(self, method: Union[str, Matcher[str]]):
        return self.with_method(method)

    def with_path(self, path: Union[furl, str, Matcher[Union[furl, URL, str]]]):
        self.path = wrap_matcher(path)
        return self

    def and_path(self, path: Union[furl, str, Matcher[Union[furl, URL, str]]]):
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

    def with_json(self, json: Union[JsonStructure, Matcher[JsonStructure]]):
        self.json = wrap_matcher(json)
        return self

    def and_json(self, json: Union[JsonStructure, JsonStructure]):
        return self.with_json(json)

    def with_times(self, times: Union[int, Matcher[int]]):
        self.times = wrap_matcher(times)
        return self

    def and_times(self, times: Union[int, Matcher[int]]):
        return self.with_times(times)


def email_sent(
    to: Union[str, Matcher[str]] = ANYTHING,
    subject: Union[str, Matcher[str]] = ANYTHING,
    body_text: Union[str, Matcher[str]] = ANYTHING,
) -> Matcher[Union[Imposter, MountebankServer]]:
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
        # TODO: builder style, & lots more attributes.
        self.body_text = wrap_matcher(body_text)
        self.subject = wrap_matcher(subject)
        self.to = wrap_matcher(
            to
        )  # TODO: Type is wrong here - to is a sequence of addresses and names.

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
            description.append_text(f" {text}: ").append_description_of(matcher)

    def describe_mismatch(
        self, actual: Union[Imposter, MountebankServer], description: Description
    ) -> None:
        sent_email = self.get_sent_email(actual)
        matching_emails = self.get_matching_emails(sent_email)

        description.append_text("found ").append_description_of(len(matching_emails))
        description.append_text(" matching emails: ").append_description_of(matching_emails)
        description.append_text(". All emails: ").append_description_of(sent_email)

    def _matches(self, actual: Union[Imposter, MountebankServer]) -> bool:
        sent_email = self.get_sent_email(actual)
        matching_emails = self.get_matching_emails(sent_email)

        return len(matching_emails) > 0

    @staticmethod
    def get_sent_email(actual) -> Sequence[SentEmail]:
        return cast(Sequence[SentEmail], list(actual.get_actual_requests()))

    def get_matching_emails(self, sent_email) -> Sequence[SentEmail]:
        return [
            email
            for email in sent_email
            if self.body_text.matches(email.text)
            and self.subject.matches(email.subject)
            and self.to.matches(email.to)
        ]
