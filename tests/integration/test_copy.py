# encoding=utf-8
import logging

import requests
from brunns.matchers.response import response_with
from hamcrest import assert_that, is_, has_entry

from mbtest.imposters import Imposter, Response, Stub, Copy, UsingRegex

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
                    Copy({"query": "name"}, "${name}", UsingRegex("AL\\w+", ignore_case=True)),
                ],
            )
        )
    )

    with mock_server(imposter):
        response = requests.get(
            '{imposter_url}/456'.format(imposter_url=imposter.url), params={"name": "Alice"}, headers={"X-REQUEST": "Header value"}
        )

        assert_that(
            response,
            is_(
                response_with(
                    status_code=456,
                    body="Hello, Alice!",
                    headers=has_entry("X-Test", "Header value"),
                )
            ),
        )
