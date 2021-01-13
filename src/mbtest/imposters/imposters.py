# encoding=utf-8
from abc import ABCMeta
from collections import abc
from enum import Enum
from typing import Iterable, Mapping, NamedTuple, Optional, Sequence, Union, cast, List

import requests
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
    :param name: Imposter name - useful for interactive exploration of imposters on http://localhost:2525/imposters
    :param record_requests: Record requests made against this imposter, so they can be asserted against later.
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
        self.host: Optional[str] = None
        self.server_url: Optional[furl] = None

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

    def get_actual_requests(self) -> Sequence["Request"]:
        json = requests.get(cast(str, self.configuration_url)).json()["requests"]
        return [Request.from_json(req) for req in json]

    def attach(self, host: str, port: int, server_url: furl) -> None:
        """Attach imposter to a running MB server."""
        self.host = host
        self.port = port
        self.server_url = server_url

    @property
    def attached(self) -> bool:
        """Imposter is attached to a running MB server."""
        return cast(bool, self.port and self.host and self.server_url)

    @property
    def configuration_url(self) -> furl:
        if self.attached:
            return cast(furl, self.server_url) / str(self.port)
        else:
            raise AttributeError(f"Unattached imposter {self} has no configuration URL.")

    def query_all_stubs(self):
        """Return all stubs running on the impostor, including those defined elsewhere."""
        json = requests.get(cast(str, self.configuration_url)).json()["stubs"]
        all_stubs = [Stub.from_structure(s) for s in json]
        return all_stubs

    def playback(self) -> Sequence[Stub]:
        all_stubs = self.query_all_stubs()
        return [s for s in all_stubs if any(not isinstance(r, Proxy) for r in s.responses)]


class GrpcImposter(Imposter):
    class Protocol(Enum):
        """Imposter `Protocol <https://github.com/cbrz/mountebank-grpc>`_."""
        GRPC = "grpc"

    def __init__(self,
                 stubs: Union[Stub, Iterable[Stub]],
                 port: Optional[int] = None,
                 name: Optional[str] = None,
                 record_requests: bool = True,
                 options: Options = None,
                 services: Services = None
                 ):
        super().__init__(
            stubs=stubs,
            port=port,
            name=name,
            record_requests=record_requests
        )

        self.protocol = GrpcImposter.Protocol.GRPC
        self.options = options
        self.services = services

    def as_structure(self) -> JsonStructure:
        structure = super().as_structure()
        if self.services:
            structure["services"] = self.services.as_structure()
        if self.options:
            structure["options"] = self.options.as_structure()
        return structure

    @classmethod
    def from_structure(cls, structure: JsonStructure) -> "GrpcImposter":
        imposter = GrpcImposter([Stub.from_structure(stub) for stub in structure["stubs"]])
        if "port" in structure:
            imposter.port = structure["port"]
        if "protocol" in structure:
            protocol = structure["protocol"]
            imposter.protocol = (
                protocol if isinstance(protocol, GrpcImposter.Protocol) else GrpcImposter.Protocol(protocol)
            )
        if "recordRequests" in structure:
            imposter.record_requests = structure["recordRequests"]
        if "name" in structure:
            imposter.name = structure["name"]
        if "services" in structure:
            imposter.services = Services.from_structure(structure["services"])
        if "options" in structure:
            imposter.options = Options.from_structure(structure["options"])
        return imposter


class Request(metaclass=ABCMeta):
    @staticmethod
    def from_json(json: JsonStructure) -> "Request":
        if "envelopeFrom" in json:
            return SentEmail.from_json(json)
        return HttpRequest.from_json(json)

    def __repr__(self) -> str:  # pragma: no cover
        state = ", ".join((f"{attr:s}={val!r:s}" for (attr, val) in vars(self).items()))
        return f"{self.__class__.__module__:s}.{self.__class__.__name__:s}({state:s})"


class HttpRequest(Request):
    def __init__(
        self,
        method: str,
        path: str,
        query: Mapping[str, str],
        headers: Mapping[str, str],
        body: str,
        **kwargs,
    ):
        self.method = method
        self.path = path
        self.query = query
        self.headers = headers
        self.body = body

    @staticmethod
    def from_json(json: JsonStructure) -> "HttpRequest":
        return HttpRequest(**json)


Address = NamedTuple("Address", [("address", str), ("name", str)])


class SentEmail(Request):
    def __init__(
        self,
        from_: Sequence[Address],
        to: Sequence[Address],
        cc: Sequence[Address],
        bcc: Sequence[Address],
        subject: str,
        text: str,
        **kwargs,
    ):
        self.from_ = from_
        self.to = to
        self.cc = cc
        self.bcc = bcc
        self.subject = subject
        self.text = text

    @staticmethod
    def from_json(json: JsonStructure) -> "SentEmail":
        email: Mapping[str, Union[str, Sequence[Address]]] = {
            SentEmail._map_key(k): SentEmail._translate_value(v) for k, v in json.items()
        }
        sent_email = SentEmail(**email)
        return sent_email

    @staticmethod
    def _map_key(key: str) -> str:
        return {"from": "from_"}.get(key, key)

    @staticmethod
    def _translate_value(value: JsonStructure) -> Union[str, Sequence[Address]]:
        if isinstance(value, str):
            return value
        elif "address" in value and "name" in value:
            return [Address(**value)]
        return [Address(**addr) if "address" in addr and "name" in addr else addr for addr in value]


def smtp_imposter(name="smtp", record_requests=True) -> Imposter:
    """Canned SMTP server imposter."""
    return Imposter(
        [], 4525, protocol=Imposter.Protocol.SMTP, name=name, record_requests=record_requests
    )


class ProtobufOptions(JsonSerializable):
    def __init__(self, include_dirs: List[str] = None):
        self.include_dirs: List[str] = include_dirs

    def as_structure(self) -> JsonStructure:
        structure = {}
        if self.include_dirs:
            structure["includeDirs"] = self.include_dirs
        return structure

    @staticmethod
    def from_structure(structure: JsonStructure) -> "ProtobufOptions":
        options = ProtobufOptions()
        if "includeDirs" in structure:
            options.includeDirs = structure["includeDirs"]
        return options


class Options(JsonSerializable):
    def __init__(self, protobufjs: ProtobufOptions = None):
        self.protobufjs: ProtobufOptions = protobufjs

    def as_structure(self) -> JsonStructure:
        structure = {}
        if self.protobufjs:
            structure["protobufjs"] = self.protobufjs.as_structure()

        return structure

    @staticmethod
    def from_structure(structure: JsonStructure) -> "Options":
        options = Options()
        if "protobufjs" in structure:
            options.protobufjs = ProtobufOptions.from_structure(structure["protobufjs"])
        return options


class Service(JsonSerializable):
    def __init__(self, name: str = "", file: str = ""):
        self.name: str = name
        self.file: str = file

    def as_structure(self):
        return {
            f"{self.name}": {
                "file": self.file
            }
        }

    @staticmethod
    def from_structure(structure: JsonStructure) -> "Service":
        service = Service()
        if "name" in structure:
            service.name = structure["name"]
        if "file" in structure:
            service.file = structure["file"]
        return service


class Services(JsonSerializable):
    def __init__(self, services: List[Service] = None):
        self.services: List[Service] = services

    def as_structure(self):
        structure = {}
        if self.services:
            for service in self.services:
                structure = {**structure, **service.as_structure()}
        return structure

    @staticmethod
    def from_structure(structure: JsonStructure) -> "Services":
        service = Services()
        if "service" in structure[""]:
            service.name = structure["name"]
        if "file" in structure:
            service.file = structure["file"]
        return service
