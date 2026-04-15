import json
import logging

import pytest
from brunns.matchers.object import has_identical_properties_to
from hamcrest import assert_that, has_entries, instance_of

from mbtest.imposters import Imposter, Proxy, Response, Stub
from mbtest.imposters.imposters import Address, SentEmail
from tests.utils.builders import (
    AndPredicateFactory,
    HttpRequestFactory,
    HttpResponseFactory,
    ImposterFactory,
    NotPredicateFactory,
    OrPredicateFactory,
)

logger = logging.getLogger(__name__)


def test_structure_port():
    expected_imposter = ImposterFactory.build(port=4546)
    imposter_structure = expected_imposter.as_structure()
    imposter = Imposter.from_structure(imposter_structure)
    assert imposter.port == 4546


def test_structure_response_port():
    expected_imposter = Imposter(Stub(responses=Response()), port=4546)
    imposter_structure = expected_imposter.as_structure()
    imposter = Imposter.from_structure(imposter_structure)
    assert imposter.port == expected_imposter.port


def test_structure_proxy_port():
    expected_imposter = Imposter(Stub(responses=Proxy("http://darwin.dog")), port=4546)
    imposter_structure = expected_imposter.as_structure()
    imposter = Imposter.from_structure(imposter_structure)
    assert imposter.port == expected_imposter.port


def test_structure_protocol():
    expected_imposter = ImposterFactory.build(protocol="http")
    imposter_structure = expected_imposter.as_structure()
    imposter = Imposter.from_structure(imposter_structure)
    assert imposter.protocol == Imposter.Protocol.HTTP


def test_structure_name():
    expected_imposter = ImposterFactory.build(name="darwin")
    imposter_structure = expected_imposter.as_structure()
    imposter = Imposter.from_structure(imposter_structure)
    assert imposter.name == "darwin"


def test_structure_record_requests():
    expected_imposter = ImposterFactory.build(record_requests=False)
    imposter_structure = expected_imposter.as_structure()
    imposter = Imposter.from_structure(imposter_structure)
    assert imposter.record_requests is False


def test_structure_no_record_requests():
    expected_imposter = Imposter(Stub())
    imposter_structure = expected_imposter.as_structure()
    del imposter_structure["recordRequests"]
    imposter = Imposter.from_structure(imposter_structure)
    assert imposter.record_requests == expected_imposter.record_requests


def test_imposter_structure_roundtrip():
    # Given
    expected = ImposterFactory.build(default_response=HttpResponseFactory.build(), port=None)
    structure = expected.as_structure()

    # When
    actual = Imposter.from_structure(structure)

    # Then
    assert_that(actual, instance_of(Imposter))
    assert_that(actual, has_identical_properties_to(expected, ignoring=["configuration_url"]))


def test_imposter_structure_without_default_response_roundtrip():
    # Given
    expected = ImposterFactory.build(default_response=None)
    structure = expected.as_structure()

    # When
    actual = Imposter.from_structure(structure)

    # Then
    assert_that(actual, instance_of(Imposter))
    assert_that(actual, has_identical_properties_to(expected, ignoring=["configuration_url"]))


@pytest.mark.parametrize("predicate", [AndPredicateFactory, OrPredicateFactory, NotPredicateFactory])
def test_imposter_complex_predicates(predicate):
    # Given
    expected = Imposter(Stub(predicate.build()))
    structure = expected.as_structure()

    # When
    actual = Imposter.from_structure(structure)

    # Then
    assert_that(actual, instance_of(Imposter))
    assert_that(actual, has_identical_properties_to(expected, ignoring=["configuration_url"]))


def test_save_and_load_roundtrip(tmp_path):
    # Given
    path = tmp_path / "imposter.json"
    original = Imposter(Stub(responses=Response()), port=4567)

    # When
    original.save(path)
    loaded = Imposter.from_file(path)

    # Then
    assert loaded.port == original.port
    assert json.loads(path.read_text())["protocol"] == "http"


def test_sent_email_from_json_with_dict_address():
    # Given - Mountebank sometimes returns a single address as a dict rather than a list
    json_data = {
        "from": {"address": "sender@example.com", "name": "Sender"},
        "to": {"address": "recipient@example.com", "name": "Recipient"},
        "subject": "Hello",
        "text": "World",
    }

    # When
    email = SentEmail.from_json(json_data)

    # Then
    assert email.to == [Address(address="recipient@example.com", name="Recipient")]


def test_http_request_roundtrip():
    # Given
    assert HttpRequestFactory.build(body="bananas").json is None
    assert HttpRequestFactory.build(body=None).json is None
    assert_that(
        HttpRequestFactory.build(body=json.dumps({"a": "b"})).json,
        has_entries(a="b"),
    )
