import logging

import httpx
from brunns.matchers.response import is_response
from hamcrest import assert_that, not_

from mbtest.imposters import Imposter, Predicate, Response, Stub
from tests.utils.data2xml import data2xml, et2string

logger = logging.getLogger(__name__)


def test_xml_response(mock_server):
    # Given
    imposter = Imposter(Stub(Predicate(), Response(body=data2xml({"foo": {"bar": "baz"}}))))

    with mock_server(imposter):
        # When
        r = httpx.get(str(imposter.url))

        # Then
        assert_that(r, is_response().with_body("<foo><bar>baz</bar></foo>"))


def test_xml_payload(mock_server):
    # Given
    imposter = Imposter(
        Stub(
            Predicate(xpath="//foo", body="bar", operator=Predicate.Operator.EQUALS),
            Response(body="sausages"),
        )
    )

    with mock_server(imposter):
        # When
        r1 = httpx.request(method="GET", url=str(imposter.url), data=et2string(data2xml({"foo": "bar"})))
        r2 = httpx.request(method="GET", url=str(imposter.url), data=et2string(data2xml({"foo": "baz"})))

        # Then
        assert_that(r1, is_response().with_body("sausages"))
        assert_that(r2, is_response().with_body(not_("sausages")))
