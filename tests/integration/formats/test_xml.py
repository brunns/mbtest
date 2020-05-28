# encoding=utf-8
import logging

import requests
from brunns.matchers.response import is_response
from hamcrest import assert_that, not_
from mbtest.imposters import Imposter, Predicate, Response, Stub
from tests.utils.data2xml import data2xml, et2string

logger = logging.getLogger(__name__)


def test_xml_response(mock_server):
    # Given
    imposter = Imposter(
        Stub(Predicate(), Response(body=data2xml({"foo": {"bar": "baz"}}))), port=4545
    )

    with mock_server(imposter):
        # When
        r = requests.get(imposter.url)

        # Then
        assert_that(r, is_response().with_body("<foo><bar>baz</bar></foo>"))


def test_xml_payload(mock_server):
    # Given
    imposter = Imposter(
        Stub(
            Predicate(xpath="//foo", body="bar", operator=Predicate.Operator.EQUALS),
            Response(body="sausages"),
        ),
        port=4545,
    )

    with mock_server(imposter):
        # When
        r1 = requests.get(imposter.url, data=et2string(data2xml({"foo": "bar"})))
        r2 = requests.get(imposter.url, data=et2string(data2xml({"foo": "baz"})))

        # Then
        assert_that(r1, is_response().with_body("sausages"))
        assert_that(r2, is_response().with_body(not_("sausages")))
