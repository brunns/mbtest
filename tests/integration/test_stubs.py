# encoding=utf-8
from __future__ import unicode_literals, absolute_import, division, print_function

import logging

import requests
from brunns.matchers.response import response_with
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
        r1 = requests.get("{0}/test1".format(imposter.url))
        r2 = requests.get("{0}/test2".format(imposter.url))

        pass
    assert_that(r1, response_with(body="sausages"))
    assert_that(r2, response_with(body="chips"))
