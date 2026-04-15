import logging

from hamcrest import assert_that, instance_of

from mbtest.imposters import Imposter, InjectionResponse, Stub
from mbtest.imposters.responses import FaultResponse, TcpResponse

logger = logging.getLogger(__name__)


def test_stub_from_structure_with_tcp_response():
    expected = Stub(responses=TcpResponse(data="hello"))
    actual = Stub.from_structure(expected.as_structure())
    assert_that(actual.responses[0], instance_of(TcpResponse))
    assert actual.responses[0].data == "hello"


def test_stub_from_structure_with_fault_response():
    expected = Stub(responses=FaultResponse(fault=FaultResponse.Fault.CONNECTION_RESET_BY_PEER))
    actual = Stub.from_structure(expected.as_structure())
    assert_that(actual.responses[0], instance_of(FaultResponse))
    assert actual.responses[0].fault == FaultResponse.Fault.CONNECTION_RESET_BY_PEER


def test_structure_inject():
    expected_imposter = Imposter(Stub(responses=InjectionResponse(inject="function (request) {\n}")), port=4546)
    imposter_structure = expected_imposter.as_structure()
    imposter = Imposter.from_structure(imposter_structure)
    assert imposter.port == expected_imposter.port
