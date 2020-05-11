# encoding=utf-8
import collections.abc as abc
from enum import Enum
from typing import Iterable, Optional, Union, cast

from furl import furl
from mbtest.imposters.base import JsonSerializable, JsonStructure
from mbtest.imposters.responses import Proxy
from mbtest.imposters.stubs import Stub


class Imposter(JsonSerializable):
    """Represents a `Mountebank imposter <http://www.mbtest.org/docs/api/mocks>`_.
    Think of an imposter as a mock website, running a protocol, on a specific port.
    Required behaviors are specified using stubs.

    :param stubs: One or more Stubs.
    :param port: Port.
    :param protocol: Protocol to run on.
    :param name: Impostor name - useful for interactive exploration of impostors on http://localhost:2525/impostors
    :param record_requests: Record requests made against this impostor, so they can be asserted against later.
    """

    class Protocol(Enum):
        """Imposter `Protocol <http://www.mbtest.org/docs/protocols/http>`_."""

        HTTP = "http"
        HTTPS = "https"
        SMTP = "smtp"
        TCP = "tcp"

    def __init__(
        self,
        stubs: Union[Stub, Iterable[Stub]],
        port: Optional[int] = None,
        protocol: Protocol = Protocol.HTTP,
        name: Optional[str] = None,
        record_requests: bool = True,
    ) -> None:
        stubs = cast(Iterable[Stub], stubs if isinstance(stubs, abc.Sequence) else [stubs])
        # For backwards compatibility where previously a proxy may have been used directly as a stub.
        self.stubs = [
            Stub(responses=cast(Proxy, stub)) if isinstance(stub, Proxy) else stub for stub in stubs
        ]
        self.port = port
        self.protocol = (
            protocol if isinstance(protocol, Imposter.Protocol) else Imposter.Protocol(protocol)
        )
        self.name = name
        self.record_requests = record_requests
        self.host = "localhost"

    @property
    def url(self) -> furl:
        return furl().set(scheme=self.protocol.value, host=self.host, port=self.port)

    def as_structure(self) -> JsonStructure:
        structure = {"protocol": self.protocol.value, "recordRequests": self.record_requests}
        if self.port:
            structure["port"] = self.port
        if self.name:
            structure["name"] = self.name
        if self.stubs:
            structure["stubs"] = [stub.as_structure() for stub in self.stubs]
        return structure

    @staticmethod
    def from_structure(structure: JsonStructure) -> "Imposter":
        imposter = Imposter([Stub.from_structure(stub) for stub in structure["stubs"]])
        if "port" in structure:
            imposter.port = structure["port"]
        if "protocol" in structure:
            protocol = structure["protocol"]
            imposter.protocol = (
                protocol if isinstance(protocol, Imposter.Protocol) else Imposter.Protocol(protocol)
            )
        if "recordRequests" in structure:
            imposter.record_requests = structure["recordRequests"]
        if "name" in structure:
            imposter.name = structure["name"]
        return imposter


def smtp_imposter(name="smtp", record_requests=True) -> Imposter:
    """Canned SMTP server impostor."""
    return Imposter(
        [], 4525, protocol=Imposter.Protocol.SMTP, name=name, record_requests=record_requests
    )
