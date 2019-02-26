# encoding=utf-8
from __future__ import unicode_literals, absolute_import, division, print_function
from six import PY3
from enum import Enum
from furl import furl

from mbtest.imposters.base import JsonSerializable
from mbtest.imposters.stubs import Stub, Proxy

if PY3:
    from collections.abc import Sequence
else:  # pragma: no cover
    from collections import Sequence


class Imposter(JsonSerializable):
    """Represents a Mountebank imposter - see http://www.mbtest.org/docs/api/mocks.
    Think of an imposter as a mock website, running a protocol, on a specific port.
    The specific behaviors require

    Pass to an :mbtest.server.mock_server:.
    """

    class Protocol(Enum):
        HTTP = "http"
        HTTPS = "https"
        SMTP = "smtp"
        TCP = "tcp"

    def __init__(self, stubs, port=None, protocol=Protocol.HTTP, name=None, record_requests=True):
        """
        :param stubs: One or more Stubs.
        :type stubs: Stub or list(Stub)
        :param port: Port.
        :type port: int
        :param protocol: :Imposter.Protocol: to run on.
        :type protocol: Imposter.Protocol
        :param name: Impostor name - useful for interactive exploration of impostors on http://localhost:2525/impostors
        :type name: str
        :param record_requests: Record requests made against this impostor, so they can be asserted against later.
        :type record_requests: bool
        """
        stubs = stubs if isinstance(stubs, Sequence) else [stubs]
        # For backwards compatability where previously a proxy may have been used directly as a stub.
        self.stubs = [Stub(responses=stub) if isinstance(stub, Proxy) else stub for stub in stubs]
        self.port = port
        self.protocol = protocol if isinstance(protocol, Imposter.Protocol) else Imposter.Protocol(protocol)
        self.name = name
        self.record_requests = record_requests

    @property
    def host(self):
        return "localhost"

    @property
    def url(self):
        return furl().set(scheme=self.protocol.value, host=self.host, port=self.port).url

    def as_structure(self):
        structure = {"protocol": self.protocol.value, "recordRequests": self.record_requests}
        if self.port:
            structure["port"] = self.port
        if self.name:
            structure["name"] = self.name
        if self.stubs:
            structure["stubs"] = [stub.as_structure() for stub in self.stubs]
        return structure

    @staticmethod
    def from_structure(structure):
        imposter = Imposter([Stub.from_structure(stub) for stub in structure["stubs"]])
        if "port" in structure:
            imposter.port = structure["port"]
        if "protocol" in structure:
            protocol = structure["protocol"]
            imposter.protocol = protocol if isinstance(protocol, Imposter.Protocol) else Imposter.Protocol(protocol)
        if "recordRequests" in structure:
            imposter.record_requests = structure["recordRequests"]
        if "name" in structure:
            imposter.name = structure["name"]
        return imposter


def smtp_imposter(name="smtp", record_requests=True):
    """Canned SMTP server impostor."""
    return Imposter([], 4525, protocol=Imposter.Protocol.SMTP, name=name, record_requests=record_requests)
