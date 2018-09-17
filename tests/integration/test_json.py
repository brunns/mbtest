# encoding=utf-8
from __future__ import unicode_literals, absolute_import, division, print_function

import logging

import pytest
import requests
from brunns.matchers.data import json_matching
from brunns.matchers.response import response_with
from hamcrest import assert_that, is_, not_

from mbtest.imposters import Imposter, Stub, Predicate, Response

logger = logging.getLogger(__name__)


@pytest.mark.usefixtures("mock_server")
def test_json_payload(mock_server):
    # Given
    imposter = Imposter(Stub(Predicate(body={"foo": ["bar", "baz"]}), Response(body="sausages")))

    with mock_server(imposter):
        # When
        r1 = requests.get(imposter.url, json={"foo": ["bar", "baz"]})
        r2 = requests.get(imposter.url, json={"baz": ["bar", "foo"]})

        # Then
        assert_that(r1, is_(response_with(body="sausages")))
        assert_that(r2, not_(response_with(body="sausages")))


@pytest.mark.usefixtures("mock_server")
def test_json_response(mock_server):
    # Given
    imposter = Imposter(Stub(Predicate(), Response(body={"foo": ["bar", "baz"]})))

    with mock_server(imposter):
        # When
        r = requests.get(imposter.url)

        # Then
        assert_that(r, is_(response_with(body=json_matching({"foo": ["bar", "baz"]}))))
