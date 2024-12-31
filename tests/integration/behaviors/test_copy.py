import logging

import httpx
from brunns.matchers.response import is_response
from hamcrest import assert_that, has_entry

from mbtest.imposters import (
    Copy,
    Imposter,
    Response,
    Stub,
    UsingJsonpath,
    UsingRegex,
    UsingXpath,
)
from tests.utils.data2xml import data2xml, et2string

logger = logging.getLogger(__name__)


def test_regex_copy(mock_server):
    imposter = Imposter(
        Stub(
            responses=Response(
                status_code="${code}",
                headers={"X-Test": "${header}"},
                body="Hello, ${name}!",
                copy=[
                    Copy("path", "${code}", UsingRegex("\\d+")),
                    Copy({"headers": "X-Request"}, "${header}", UsingRegex(".+")),
                    Copy(
                        {"query": "name"},
                        "${name}",
                        UsingRegex("AL\\w+", ignore_case=True),
                    ),
                ],
            )
        )
    )

    with mock_server(imposter):
        response = httpx.get(
            str(imposter.url / str(456)), params={"name": "Alice"}, headers={"X-REQUEST": "Header value"}
        )

        assert_that(
            response,
            is_response()
            .with_status_code(456)
            .with_body("Hello, Alice!")
            .with_headers(has_entry("x-test", "Header value")),
        )


def test_xpath_copy(mock_server):
    imposter = Imposter(
        Stub(responses=Response(body="Have you read BOOK?", copy=Copy("body", "BOOK", UsingXpath("(//title)[2]"))))
    )

    with mock_server(imposter):
        response = httpx.post(str(imposter.url), data=BOOKS_XML)

        assert_that(response, is_response().with_body("Have you read Harry Potter?"))


def test_xpath_copy_namespaced(mock_server):
    imposter = Imposter(
        Stub(
            responses=Response(
                body="Have you read BOOK?",
                copy=Copy(
                    "body",
                    "BOOK",
                    UsingXpath(
                        "//isbn:title",
                        ns={"isbn": "http://schemas.isbn.org/ns/1999/basic.dtd"},
                    ),
                ),
            )
        )
    )

    with mock_server(imposter):
        response = httpx.post(str(imposter.url), data=BOOKS_XML_NAMESPACED)

        assert_that(response, is_response().with_body("Have you read Game of Thrones?"))


def test_jsonpath_copy(mock_server):
    imposter = Imposter(
        Stub(
            responses=Response(
                body="Have you read BOOK?",
                copy=Copy("body", "BOOK", UsingJsonpath("$..title")),
            )
        )
    )

    with mock_server(imposter):
        response = httpx.post(
            str(imposter.url),
            json={
                "books": [
                    {
                        "book": {
                            "title": "Game of Thrones",
                            "summary": "Dragons and political intrigue",
                        }
                    },
                    {
                        "book": {
                            "title": "Harry Potter",
                            "summary": "Dragons and a boy wizard",
                        }
                    },
                    {
                        "book": {
                            "title": "The Hobbit",
                            "summary": "A dragon and short people",
                        }
                    },
                ]
            },
        )

        assert_that(response, is_response().with_body("Have you read Game of Thrones?"))


BOOKS_XML = et2string(
    data2xml(
        {
            "books": [
                {
                    "book": {
                        "title": "Game of Thrones",
                        "summary": "Dragons and political intrigue",
                    }
                },
                {
                    "book": {
                        "title": "Harry Potter",
                        "summary": "Dragons and a boy wizard",
                    }
                },
                {
                    "book": {
                        "title": "The Hobbit",
                        "summary": "A dragon and short people",
                    }
                },
            ]
        }
    )
)
BOOKS_XML_NAMESPACED = et2string(
    data2xml(
        {
            "books": [
                {
                    "book": {
                        "isbn:title": "Game of Thrones",
                        "isbn:summary": "Dragons and political intrigue",
                    }
                },
                {
                    "book": {
                        "isbn:title": "Harry Potter",
                        "isbn:summary": "Dragons and a boy wizard",
                    }
                },
                {
                    "book": {
                        "isbn:title": "The Hobbit",
                        "isbn:summary": "A dragon and short people",
                    }
                },
            ]
        },
        default_namespace=("isbn", "http://schemas.isbn.org/ns/1999/basic.dtd"),
    )
)
