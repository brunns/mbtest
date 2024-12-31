from collections import abc
from collections.abc import Iterable, Mapping, Sequence
from enum import Enum
from json import JSONDecodeError, loads
from typing import NamedTuple, Optional, Union, cast

import httpx
from yarl import URL

from mbtest.imposters.base import JsonSerializable, JsonStructure
from mbtest.imposters.responses import HttpResponse, Proxy
from mbtest.imposters.stubs import AddStub, Stub


class Imposter(JsonSerializable):
    """Represents a `Mountebank imposter <http://www.mbtest.org/docs/api/mocks>`_.
    Think of an imposter as a mock website, running a protocol, on a specific port.
    Required behaviors are specified using stubs.

    :param stubs: One or more Stubs.
    :param port: Port.
    :param protocol: Protocol to run on.
    :param name: Imposter name - useful for interactive exploration of imposters on http://localhost:2525/imposters
    :param default_response: The default response to send if no predicate matches.
    :param record_requests: Record requests made against this imposter, so they can be asserted against later.
    :param mutual_auth: Server will request a client certificate.
    :param key: SSL server certificate.
    :param cert: SSL server certificate.
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
        default_response: Optional[HttpResponse] = None,
        record_requests: bool = True,  # noqa: FBT001,FBT002
        mutual_auth: bool = False,  # noqa: FBT001,FBT002
        key: Optional[str] = None,
        cert: Optional[str] = None,
    ) -> None:
        stubs = cast(Iterable[Stub], stubs if isinstance(stubs, abc.Sequence) else [stubs])
        # For backwards compatibility where previously a proxy may have been used directly as a stub.
        self.stubs = [Stub(responses=cast(Proxy, stub)) if isinstance(stub, Proxy) else stub for stub in stubs]
        self.port = port
        self.protocol = protocol if isinstance(protocol, Imposter.Protocol) else Imposter.Protocol(protocol)
        self.name = name
        self.default_response = default_response
        self.record_requests = record_requests
        self.host: Optional[str] = None
        self.server_url: Optional[URL] = None
        self.mutual_auth = mutual_auth
        self.key = key
        self.cert = cert

    @property
    def url(self) -> Optional[URL]:
        if self.host:
            return URL.build(scheme=self.protocol.value, host=self.host, port=self.port)
        return None

    def as_structure(self) -> JsonStructure:
        structure = {"protocol": self.protocol.value, "recordRequests": self.record_requests}
        self.add_if_true(structure, "port", self.port)
        self.add_if_true(structure, "name", self.name)
        if self.default_response:
            structure["defaultResponse"] = self.default_response.as_structure()
        self.add_if_true(structure, "stubs", [stub.as_structure() for stub in self.stubs])
        self.add_if_true(structure, "mutualAuth", self.mutual_auth)
        self.add_if_true(structure, "key", self.key)
        self.add_if_true(structure, "cert", self.cert)
        return structure

    @classmethod
    def from_structure(cls, structure: JsonStructure) -> "Imposter":
        imposter = cls([Stub.from_structure(stub) for stub in structure["stubs"]])
        imposter.set_if_in_dict(structure, "port", "port")
        imposter.protocol = cls.Protocol(structure["protocol"])
        imposter.set_if_in_dict(structure, "name", "name")
        if "defaultResponse" in structure:
            imposter.default_response = HttpResponse.from_structure(structure["defaultResponse"])
        imposter.set_if_in_dict(structure, "recordRequests", "record_requests")
        imposter.set_if_in_dict(structure, "mutualAuth", "mutual_auth")
        imposter.set_if_in_dict(structure, "key", "key")
        imposter.set_if_in_dict(structure, "cert", "cert")
        return imposter

    def get_actual_requests(self) -> Sequence["Request"]:
        json = httpx.get(str(self.configuration_url)).json()["requests"]
        return [Request.from_json(req) for req in json]

    def attach(self, host: str, port: int, server_url: URL) -> None:
        """Attach imposter to a running MB server."""
        self.host = host
        self.port = port
        self.server_url = server_url

    @property
    def attached(self) -> bool:
        """Imposter is attached to a running MB server."""
        return cast(bool, self.port and self.host and self.server_url)

    @property
    def configuration_url(self) -> URL:
        if self.attached:
            return cast(URL, self.server_url) / str(self.port)
        msg = f"Unattached imposter {self} has no configuration URL."
        raise AttributeError(msg)

    def query_all_stubs(self) -> list[Stub]:
        """Return all stubs running on the impostor, including those defined elsewhere."""
        json = httpx.get(str(self.configuration_url)).json()["stubs"]
        return [Stub.from_structure(s) for s in json]

    def playback(self) -> list[Stub]:
        all_stubs = self.query_all_stubs()
        return [s for s in all_stubs if any(not isinstance(r, Proxy) for r in s.responses)]

    def add_stubs(self, definition: Union[Stub, Iterable[Stub]], index: Optional[int] = None) -> None:
        """Add one or more stubs to a running impostor."""
        if isinstance(definition, abc.Iterable):
            for stub in definition:
                self.add_stubs(stub)
        else:
            self.add_stub(definition, index)

    def add_stub(self, definition: Stub, index: Optional[int] = None) -> int:
        """Add a stub to a running impostor. Returns index of new stub."""
        json = AddStub(stub=definition, index=index).as_structure()
        post = httpx.post(f"{self.configuration_url}/stubs", json=json)
        post.raise_for_status()
        self.stubs.append(definition)  # TODO - what if we've not added to the end?
        return index or len(post.json()["stubs"]) - 1

    def delete_stub(self, index: int) -> Stub:
        """Remove a stub from a running impostor."""
        post = httpx.delete(f"{self.configuration_url}/stubs/{index}")
        post.raise_for_status()
        return self.stubs.pop(index)

    def update_stub(self, index: int, definition: Stub) -> int:
        """Change a stub in an existing imposter. Returns index of changed stub."""
        json = definition.as_structure()
        put = httpx.put(f"{self.configuration_url}/stubs/{index}", json=json)
        put.raise_for_status()
        return index


class Request:
    @staticmethod
    def from_json(json: JsonStructure) -> "Request":
        if "envelopeFrom" in json:
            return SentEmail.from_json(json)
        return HttpRequest.from_json(json)

    def __repr__(self) -> str:  # pragma: no cover
        state = ", ".join(f"{attr:s}={val!r:s}" for (attr, val) in vars(self).items())
        return f"{self.__class__.__module__:s}.{self.__class__.__name__:s}({state:s})"


class HttpRequest(Request):
    def __init__(
        self,
        method: str,
        path: str,
        query: Mapping[str, str],
        headers: Mapping[str, str],
        body: str,
        **kwargs,  # noqa: ARG002
    ):
        self.method = method
        self.path = path
        self.query = query
        self.headers = headers
        self.body = body

    @staticmethod
    def from_json(json: JsonStructure) -> "HttpRequest":
        return HttpRequest(**json)

    @property
    def json(self):
        try:
            return loads(self.body) if self.body else None
        except JSONDecodeError:
            return None


class Address(NamedTuple):
    address: str
    name: str


class SentEmail(Request):
    def __init__(
        self,
        from_: Sequence[Address],
        to: Sequence[Address],
        cc: Sequence[Address],
        bcc: Sequence[Address],
        subject: str,
        text: str,
        **kwargs,  # noqa: ARG002
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
        return SentEmail(**email)  # type: ignore[arg-type]

    @staticmethod
    def _map_key(key: str) -> str:
        return {"from": "from_"}.get(key, key)

    @staticmethod
    def _translate_value(value: JsonStructure) -> Union[str, Sequence[Address]]:
        if isinstance(value, str):
            return value
        if "address" in value and "name" in value:
            return [Address(**value)]
        return [Address(**addr) if "address" in addr and "name" in addr else addr for addr in value]


def smtp_imposter(name="smtp", *, record_requests=True) -> Imposter:
    """Canned SMTP server imposter."""
    return Imposter([], 5525, protocol=Imposter.Protocol.SMTP, name=name, record_requests=record_requests)
