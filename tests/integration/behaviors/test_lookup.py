# encoding=utf-8
import logging
from pathlib import Path

import requests
from brunns.matchers.response import is_response
from hamcrest import assert_that, has_entry

from mbtest.imposters import Imposter, Key, Lookup, Response, Stub, UsingRegex

logger = logging.getLogger(__name__)


def test_lookup(mock_server):
    datasource_path = str(Path("tests") / "integration" / "behaviors" / "test_data" / "values.csv")
    imposter = Imposter(
        Stub(
            responses=Response(
                status_code="${row}['code']",
                body="Hello ${row}['Name'], have you done your ${row}['jobs'] today?",
                headers={"X-Tree": "${row}['tree']"},
                lookup=Lookup(
                    Key("path", UsingRegex("/(.*)$"), 1), datasource_path, "Name", "${row}"
                ),
            )
        )
    )

    with mock_server(imposter):
        response = requests.get(imposter.url / "liquid")

        assert_that(
            response,
            is_response()
            .with_status_code(400)
            .with_body("Hello liquid, have you done your farmer today?")
            .with_headers(has_entry("X-Tree", "mango")),
        )


def test_lookup_with_Path_type(mock_server):
    datasource_path = Path("tests") / "integration" / "behaviors" / "test_data" / "values.csv"
    imposter = Imposter(
        Stub(
            responses=Response(
                status_code="${row}['code']",
                body="Hello ${row}['Name'], have you done your ${row}['jobs'] today?",
                headers={"X-Tree": "${row}['tree']"},
                lookup=Lookup(
                    Key("path", UsingRegex("/(.*)$"), 1), datasource_path, "Name", "${row}"
                ),
            )
        )
    )

    with mock_server(imposter):
        response = requests.get(imposter.url / "liquid")

        assert_that(
            response,
            is_response()
            .with_status_code(400)
            .with_body("Hello liquid, have you done your farmer today?")
            .with_headers(has_entry("X-Tree", "mango")),
        )
