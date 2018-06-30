import logging

import pytest
import requests
from hamcrest import assert_that

from matchers.request import has_request
from matchers.response import has_body_containing, has_status_code
from mb.imposters import Imposter, Predicate, Response, Stub

logger = logging.getLogger(__name__)


@pytest.mark.usefixtures("mock_server")
def test_1_imposter(mock_server):
    imposter = Imposter(Stub(Predicate(path="/test"), Response("sausages")), record_requests=True)

    with mock_server(imposter) as s:
        logger.debug("server: %s", s)
        r = requests.get("{}/test".format(imposter.url))

        assert r.text == "sausages"
        assert_that(s, has_request(path="/test", method="GET"))

    assert_that(r, has_status_code(200))
    assert_that(r, has_body_containing("sausages"))


@pytest.mark.usefixtures("mock_server")
def test_2_imposters(mock_server):
    imposters = [
        Imposter(Stub(Predicate(path="/test1"), Response("sausages")), port=4567, name="bill"),
        Imposter([Stub([Predicate(path="/test2")], [Response("chips", status_code=201)])], port=4568),
    ]

    with mock_server(imposters) as s:
        logger.debug("server: %s", s)
        r1 = requests.get("{}/test1".format(imposters[0].url))
        r2 = requests.get("{}/test2".format(imposters[1].url))

    assert_that(r1, has_status_code(200))
    assert_that(r1, has_body_containing("sausages"))
    assert_that(r2, has_status_code(201))
    assert_that(r2, has_body_containing("chips"))
