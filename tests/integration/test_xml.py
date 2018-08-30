import logging

import pytest
import requests
from brunns.matchers.response import response_with
from hamcrest import assert_that, is_, not_

from mbtest.imposters import Imposter, Stub, Predicate, Response
from tests.utils.data2xml import data2xml, et2string

logger = logging.getLogger(__name__)


@pytest.mark.usefixtures("mock_server")
def test_xml_response(mock_server):
    # Given
    imposter = Imposter(Stub(Predicate(), Response(body=data2xml({"foo": {"bar": "baz"}}))))

    with mock_server(imposter):
        # When
        r = requests.get(imposter.url)

        # Then
        assert_that(r, is_(response_with(body="<foo><bar>baz</bar></foo>")))


@pytest.mark.usefixtures("mock_server")
def test_xml_payload(mock_server):
    # Given
    imposter = Imposter(
        Stub(Predicate(xpath="//foo", body="bar", operator=Predicate.Operator.EQUALS), Response(body="sausages"))
    )

    with mock_server(imposter):
        # When
        r1 = requests.get(imposter.url, data=et2string(data2xml({"foo": "bar"})))
        r2 = requests.get(imposter.url, data=et2string(data2xml({"foo": "baz"})))

        # Then
        assert_that(r1, is_(response_with(body="sausages")))
        assert_that(r2, is_(response_with(body=not_("sausages"))))
