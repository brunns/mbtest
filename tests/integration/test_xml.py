import logging

import pytest
import requests
from hamcrest import assert_that, is_

from matchers.response import response_with
from mbtest.imposters import Imposter, Stub, Predicate, Response
from tests.utils.data2xml import data2xml

logger = logging.getLogger(__name__)


@pytest.mark.usefixtures("mock_server")
def test_xml_response(mock_server):
    # Given
    body = data2xml({"foo": {"bar": "baz"}})
    imposter = Imposter(Stub(Predicate(), Response(body=body)))

    with mock_server(imposter):
        # When
        r = requests.get(imposter.url)

        # Then
        assert_that(r, is_(response_with(body="<foo><bar>baz</bar></foo>")))
