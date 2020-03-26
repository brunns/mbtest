# encoding=utf-8
import logging

import requests
from brunns.matchers.response import is_response
from hamcrest import assert_that
from mbtest.imposters import Imposter, Predicate, Response, Stub

logger = logging.getLogger(__name__)


def test_multiple_imposters(mock_server):
    imposters = [
        Imposter(Stub(Predicate(path="/test1"), Response("sausages"))),
        Imposter([Stub([Predicate(path="/test2")], [Response("chips", status_code=201)])]),
    ]

    with mock_server(imposters) as s:
        logger.debug("server: %s", s)
        r1 = requests.get("{0}/test1".format(imposters[0].url))
        r2 = requests.get("{0}/test2".format(imposters[1].url))

    assert_that(r1, is_response().with_status_code(200).and_body("sausages"))
    assert_that(r2, is_response().with_status_code(201).and_body("chips"))


def test_default_imposter(mock_server):
    imposter = Imposter(Stub())

    with mock_server(imposter) as s:
        logger.debug("server: %s", s)
        r = requests.get("{0}/".format(imposter.url))

    assert_that(r, is_response().with_status_code(200).and_body(""))
