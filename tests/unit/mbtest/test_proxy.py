# encoding=utf-8
import logging

from mbtest.imposters import Proxy
from tests.utils.builders import ProxyBuilder

logger = logging.getLogger(__name__)


def test_structure_to():
    expected_proxy = ProxyBuilder().build()
    proxy_structure = expected_proxy.as_structure()
    proxy = Proxy.from_structure(proxy_structure)
    assert proxy.to == expected_proxy.to


def test_structure_wait():
    expected_proxy = ProxyBuilder().with_wait(200).build()
    proxy_structure = expected_proxy.as_structure()
    proxy = Proxy.from_structure(proxy_structure)
    assert proxy.wait == expected_proxy.wait


def test_structure_inject_headers():
    expected_proxy = (
        ProxyBuilder().with_inject_headers({"X-Clacks-Overhead": "GNU Terry Pratchett"}).build()
    )
    proxy_structure = expected_proxy.as_structure()
    proxy = Proxy.from_structure(proxy_structure)
    assert proxy.inject_headers == expected_proxy.inject_headers


def test_structure_mode():
    expected_proxy = ProxyBuilder().with_mode(Proxy.Mode.TRANSPARENT).build()
    proxy_structure = expected_proxy.as_structure()
    proxy = Proxy.from_structure(proxy_structure)
    assert proxy.mode == expected_proxy.mode
