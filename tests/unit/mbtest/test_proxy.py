import logging

from mbtest.imposters import Proxy
from mbtest.imposters.responses import BaseResponse
from tests.utils.builders import ProxyFactory

logger = logging.getLogger(__name__)


def test_structure_to():
    expected_proxy = ProxyFactory.build()
    proxy_structure = expected_proxy.as_structure()
    proxy = BaseResponse.from_structure(proxy_structure)
    assert proxy.to == expected_proxy.to


def test_structure_wait():
    expected_proxy = ProxyFactory.build(wait=200)
    proxy_structure = expected_proxy.as_structure()
    proxy = BaseResponse.from_structure(proxy_structure)
    assert proxy.wait == expected_proxy.wait


def test_structure_inject_headers():
    expected_proxy = ProxyFactory.build(inject_headers={"X-Clacks-Overhead": "GNU Terry Pratchett"})
    proxy_structure = expected_proxy.as_structure()
    proxy = BaseResponse.from_structure(proxy_structure)
    assert proxy.inject_headers == expected_proxy.inject_headers


def test_structure_mode():
    expected_proxy = ProxyFactory.build(mode=Proxy.Mode.TRANSPARENT)
    proxy_structure = expected_proxy.as_structure()
    proxy = BaseResponse.from_structure(proxy_structure)
    assert proxy.mode == expected_proxy.mode


def test_structure_decorate():
    expected_proxy = ProxyFactory.build(decorate="(req, res) => {}")
    proxy_structure = expected_proxy.as_structure()
    proxy = BaseResponse.from_structure(proxy_structure)
    assert proxy.decorate == expected_proxy.decorate
