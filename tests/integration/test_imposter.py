# encoding=utf-8
from __future__ import absolute_import, division, print_function, unicode_literals

import logging

from mbtest.imposters import Imposter, Stub, Proxy, Response

logger = logging.getLogger(__name__)


def test_structure_port():
    expected_imposter = Imposter(Stub(), port=4546)
    imposter_structure = expected_imposter.as_structure()
    imposter = Imposter.from_structure(imposter_structure)
    assert imposter.port == expected_imposter.port


def test_structure_no_port():
    expected_imposter = Imposter(Stub())
    imposter_structure = expected_imposter.as_structure()
    imposter = Imposter.from_structure(imposter_structure)
    assert imposter.port == expected_imposter.port


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
    expected_imposter = Imposter(Stub(), protocol="http")
    imposter_structure = expected_imposter.as_structure()
    imposter = Imposter.from_structure(imposter_structure)
    assert imposter.protocol == expected_imposter.protocol


def test_structure_no_protocol():
    expected_imposter = Imposter(Stub())
    imposter_structure = expected_imposter.as_structure()
    del imposter_structure["protocol"]
    imposter = Imposter.from_structure(imposter_structure)
    assert imposter.protocol == expected_imposter.protocol


def test_structure_name():
    expected_imposter = Imposter(Stub(), name="darwin")
    imposter_structure = expected_imposter.as_structure()
    imposter = Imposter.from_structure(imposter_structure)
    assert imposter.name == expected_imposter.name


def test_structure_record_requests():
    expected_imposter = Imposter(Stub(), record_requests=False)
    imposter_structure = expected_imposter.as_structure()
    imposter = Imposter.from_structure(imposter_structure)
    assert imposter.record_requests == expected_imposter.record_requests


def test_structure_no_record_requests():
    expected_imposter = Imposter(Stub())
    imposter_structure = expected_imposter.as_structure()
    del imposter_structure["recordRequests"]
    imposter = Imposter.from_structure(imposter_structure)
    assert imposter.record_requests == expected_imposter.record_requests
