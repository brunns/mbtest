# encoding=utf-8
import logging

from mbtest.imposters import Proxy

logger = logging.getLogger(__name__)


def test_structure_to():
    expected_proxy = Proxy("http://darwin.dog")
    proxy_structure = expected_proxy.as_structure()
    proxy = Proxy.from_structure(proxy_structure)
    assert proxy.to == expected_proxy.to


def test_structure_wait():
    expected_proxy = Proxy("http://darwin.dog", wait=200)
    proxy_structure = expected_proxy.as_structure()
    proxy = Proxy.from_structure(proxy_structure)
    assert proxy.wait == expected_proxy.wait


def test_structure_inject_headers():
    expected_proxy = Proxy(
        "http://darwin.dog", inject_headers={"X-Clacks-Overhead": "GNU Terry Pratchett"}
    )
    proxy_structure = expected_proxy.as_structure()
    proxy = Proxy.from_structure(proxy_structure)
    assert proxy.inject_headers == expected_proxy.inject_headers
