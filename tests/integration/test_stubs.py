# encoding=utf-8
import logging

import requests
from brunns.matchers.response import is_response
from hamcrest import assert_that

from mbtest.imposters import Imposter, Predicate, Response, Stub

logger = logging.getLogger(__name__)


def test_multiple_stubs(mock_server):
    imposter = Imposter(
        [
            Stub(Predicate(path="/test1"), Response(body="sausages")),
            Stub(Predicate(path="/test2"), Response(body="chips")),
        ],
        port=4567,
        name="bill",
    )

    with mock_server(imposter) as s:
        logger.debug("server: %s", s)
        r1 = requests.get(f"{imposter.url}/test1")
        r2 = requests.get(f"{imposter.url}/test2")

    assert_that(r1, is_response().with_body("sausages"))
    assert_that(r2, is_response().with_body("chips"))
