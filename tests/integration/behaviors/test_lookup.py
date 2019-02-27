# encoding=utf-8
import logging
import requests
from brunns.matchers.response import response_with
from hamcrest import assert_that, is_, has_entry

try:
    from pathlib import Path
except ImportError:
    from pathlib2 import Path

from mbtest.imposters import Imposter, Response, Stub, Lookup, Key, UsingRegex

logger = logging.getLogger(__name__)


def test_lookup(mock_server):
    datasource_path = str(Path("tests") / "integration" / "behaviors" / "test_data" / "values.csv")
    imposter = Imposter(
        Stub(
            responses=Response(
                status_code="${row}['code']",
                body="Hello ${row}['Name'], have you done your ${row}['jobs'] today?",
                headers={"X-Tree": "${row}['tree']"},
                lookup=Lookup(Key("path", UsingRegex("/(.*)$"), 1), datasource_path, "Name", "${row}"),
            )
        )
    )

    with mock_server(imposter):
        response = requests.get("{imposter_url}/liquid".format(imposter_url=imposter.url))

        assert_that(
            response,
            is_(
                response_with(
                    status_code=400,
                    body="Hello liquid, have you done your farmer today?",
                    headers=has_entry("X-Tree", "mango"),
                )
            ),
        )
