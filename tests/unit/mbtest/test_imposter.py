# encoding=utf-8
import logging

from brunns.matchers.object import has_identical_properties_to
from hamcrest import assert_that, instance_of

from mbtest.imposters import Imposter, Proxy, Response, Stub
from tests.utils.builders import ImposterBuilder

logger = logging.getLogger(__name__)


def test_structure_port():
    expected_imposter = ImposterBuilder().with_port(4546).build()
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
    expected_imposter = ImposterBuilder().with_protocol("http").build()
    imposter_structure = expected_imposter.as_structure()
    imposter = Imposter.from_structure(imposter_structure)
    assert imposter.protocol == Imposter.Protocol.HTTP


def test_structure_name():
    expected_imposter = ImposterBuilder().with_name("darwin").build()
    imposter_structure = expected_imposter.as_structure()
    imposter = Imposter.from_structure(imposter_structure)
    assert imposter.name == "darwin"


def test_structure_record_requests():
    expected_imposter = ImposterBuilder().with_record_requests(False).build()
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
    expected = ImposterBuilder().build()
    structure = expected.as_structure()

    # When
    actual = Imposter.from_structure(structure)

    # Then
    assert_that(actual, instance_of(Imposter))
    assert_that(actual, has_identical_properties_to(expected, ignoring="configuration_url"))
