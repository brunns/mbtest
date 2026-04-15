from __future__ import annotations

from collections import abc
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from enum import Enum
from json import JSONDecodeError, dumps, loads
from pathlib import Path
from typing import cast

import httpx
from yarl import URL

from mbtest.imposters.base import JsonSerializable, JsonStructure
from mbtest.imposters.responses import HttpResponse, Proxy
from mbtest.imposters.stubs import AddStub, Stub


@dataclass(init=False)
class Imposter(JsonSerializable):
    """Represents a `Mountebank imposter <http://localhost:2525/docs/api/mocks>`_.
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
        """Imposter `Protocol <http://localhost:2525/docs/protocols/http>`_."""

        HTTP = "http"
        HTTPS = "https"
        SMTP = "smtp"
        TCP = "tcp"

    stubs: list[Stub]
    port: int | None = None
    protocol: Imposter.Protocol = Protocol.HTTP
    name: str | None = None
    default_response: HttpResponse | None = None
    record_requests: bool = True
    mutual_auth: bool = False
    key: str | None = None
    cert: str | None = None
    host: str | None = field(default=None, repr=False, compare=False)
    server_url: URL | None = field(default=None, repr=False, compare=False)

    def __init__(
        self,
        stubs: Stub | Iterable[Stub],
        port: int | None = None,
        protocol: Imposter.Protocol | str = Protocol.HTTP,
        name: str | None = None,
        default_response: HttpResponse | None = None,
        key: str | None = None,
        cert: str | None = None,
        *,
        record_requests: bool = True,
        mutual_auth: bool = False,
        host: str | None = None,
        server_url: URL | None = None,
    ) -> None:
        stubs_iter = cast("Iterable[Stub]", stubs if isinstance(stubs, abc.Sequence) else [stubs])
        # For backwards compatibility where previously a proxy may have been used directly as a stub.
        self.stubs = [Stub(responses=cast("Proxy", stub)) if isinstance(stub, Proxy) else stub for stub in stubs_iter]
        self.port = port
        self.protocol = protocol if isinstance(protocol, Imposter.Protocol) else Imposter.Protocol(protocol)
        self.name = name
        self.default_response = default_response
        self.record_requests = record_requests
        self.mutual_auth = mutual_auth
        self.key = key
        self.cert = cert
        self.host = host
        self.server_url = server_url

    @property
    def url(self) -> URL | None:
        if self.host:
            return URL.build(scheme=self.protocol.value, host=self.host, port=self.port)
        return None

    def as_structure(self) -> JsonStructure:
        structure: dict[str, JsonStructure] = {"protocol": self.protocol.value, "recordRequests": self.record_requests}
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
    def from_structure(cls, structure: JsonStructure) -> Imposter:
        return cls(
            stubs=[Stub.from_structure(stub) for stub in structure["stubs"]],
            port=structure.get("port"),
            protocol=structure["protocol"],
            name=structure.get("name"),
            default_response=HttpResponse.from_structure(structure["defaultResponse"])
            if "defaultResponse" in structure
            else None,
            record_requests=structure.get("recordRequests", True),
            mutual_auth=structure.get("mutualAuth", False),
            key=structure.get("key"),
            cert=structure.get("cert"),
        )

    def save(self, path: Path | str) -> None:
        """Save this imposter to a JSON file for later replay.

        The saved file can be loaded with :meth:`from_file` and posted to a
        Mountebank server, or used directly with Mountebank's ``--configfile`` option.

        :param path: Destination file path.
        """
        Path(path).write_text(dumps(self.as_structure(), indent=2))

    @classmethod
    def from_file(cls, path: Path | str) -> Imposter:
        """Load an imposter from a JSON file previously saved with :meth:`save`.

        :param path: Source file path.
        :returns: An Imposter object.
        """
        return cls.from_structure(loads(Path(path).read_text()))

    def get_actual_requests(self) -> Sequence[Request]:
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
        return cast("bool", self.port and self.host and self.server_url)

    @property
    def configuration_url(self) -> URL:
        if self.attached:
            return cast("URL", self.server_url) / str(self.port)
        msg = f"Unattached imposter {self} has no configuration URL."
        raise AttributeError(msg)

    def query_all_stubs(self) -> list[Stub]:
        """Return all stubs running on the impostor, including those defined elsewhere."""
        json = httpx.get(str(self.configuration_url)).json()["stubs"]
        return [Stub.from_structure(s) for s in json]

    def playback(self) -> list[Stub]:
        all_stubs = self.query_all_stubs()
        return [s for s in all_stubs if any(not isinstance(r, Proxy) for r in s.responses)]

    def add_stubs(self, definition: Stub | Iterable[Stub], index: int | None = None) -> None:
        """Add one or more stubs to a running impostor."""
        if isinstance(definition, abc.Iterable):
            for stub in definition:
                self.add_stubs(stub)
        else:
            self.add_stub(definition, index)

    def add_stub(self, definition: Stub, index: int | None = None) -> int:
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
    def from_json(json: JsonStructure) -> Request:
        if "envelopeFrom" in json:
            return SentEmail.from_json(json)
        return HttpRequest.from_json(json)


@dataclass
class HttpRequest(Request):
    method: str
    path: str
    query: Mapping[str, str]
    headers: Mapping[str, str]
    body: str | None = None

    @staticmethod
    def from_json(json: JsonStructure) -> HttpRequest:
        return HttpRequest(
            method=json["method"],
            path=json["path"],
            query=json.get("query", {}),
            headers=json.get("headers", {}),
            body=json.get("body"),
        )

    @property
    def json(self) -> JsonStructure | None:
        try:
            return loads(self.body) if self.body else None
        except JSONDecodeError:
            return None


@dataclass
class Address:
    address: str
    name: str


@dataclass
class SentEmail(Request):
    from_: Address
    to: list[Address]
    cc: list[Address]
    bcc: list[Address]
    subject: str
    text: str

    @staticmethod
    def from_json(json: JsonStructure) -> SentEmail:
        return SentEmail(
            from_=Address(**json["from"]) if isinstance(json.get("from"), dict) else Address(address="", name=""),
            to=SentEmail._parse_addresses(json.get("to", [])),
            cc=SentEmail._parse_addresses(json.get("cc", [])),
            bcc=SentEmail._parse_addresses(json.get("bcc", [])),
            subject=json.get("subject", ""),
            text=json.get("text", ""),
        )

    @staticmethod
    def _parse_addresses(value: JsonStructure) -> list[Address]:
        if isinstance(value, dict):
            return [Address(**value)]
        return [Address(**addr) if isinstance(addr, dict) else addr for addr in value]


def smtp_imposter(name: str = "smtp", *, record_requests: bool = True) -> Imposter:
    """Canned SMTP server imposter."""
    return Imposter([], 5525, protocol=Imposter.Protocol.SMTP, name=name, record_requests=record_requests)
