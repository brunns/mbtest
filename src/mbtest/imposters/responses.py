from __future__ import annotations

from abc import ABC
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from enum import Enum
from http import HTTPStatus
from typing import cast
from xml.etree import ElementTree as ET  # nosec - We are creating, not parsing XML.

from yarl import URL

from mbtest.imposters.base import Injecting, JsonObject, JsonSerializable, JsonValue
from mbtest.imposters.behaviors import Copy, Lookup
from mbtest.imposters.predicates import Predicate


@dataclass
class BaseResponse(JsonSerializable, ABC):
    @classmethod
    def from_structure(cls, structure: JsonObject) -> BaseResponse:  # noqa: C901
        if "is" in structure and "data" in cls.as_json_object(structure["is"]):
            return TcpResponse.from_structure(structure)
        if "is" in structure:
            return Response.from_structure(structure)
        if "proxy" in structure:
            return Proxy.from_structure(structure)
        if "inject" in structure:
            return InjectionResponse.from_structure(structure)
        if "fault" in structure:
            return FaultResponse.from_structure(structure)
        raise NotImplementedError  # pragma: no cover


@dataclass(init=False)
class HttpResponse(JsonSerializable):
    """Represents a `Mountebank HTTP response <http://localhost:2525/docs/protocols/http>`_.

    :param body: Body text for response. Can be a string, bytes, an XML Element, or a JSON serialisable data structure.
    :param status_code: HTTP status code - prefer :class:`http.HTTPStatus` values.
    :param headers: Response HTTP headers
    :param mode: Mode - text or binary

    """

    body: str | JsonObject | ET.Element | bytes = ""
    status_code: HTTPStatus | int | str = HTTPStatus.OK
    headers: Mapping[str, str] | None = None
    mode: Response.Mode

    def __init__(
        self,
        body: str | JsonObject | ET.Element | bytes = "",
        status_code: HTTPStatus | int | str = HTTPStatus.OK,
        headers: Mapping[str, str] | None = None,
        mode: Response.Mode | None = None,
    ) -> None:
        self.body = body
        self.status_code = status_code
        self.headers = headers
        self.mode = mode if mode is not None else Response.Mode.TEXT

    def as_structure(self) -> JsonObject:
        if isinstance(self.body, ET.Element):
            body_str: str | JsonObject = ET.tostring(self.body, encoding="unicode")
        elif isinstance(self.body, bytes):
            body_str = self.body.decode("utf-8")
        else:
            body_str = self.body
        is_structure: JsonObject = {"statusCode": self.status_code, "_mode": self.mode.value}
        self.add_if_true(is_structure, "body", body_str)
        self.add_if_true(is_structure, "headers", self.headers)
        return is_structure

    @classmethod
    def from_structure(cls, structure: JsonObject) -> HttpResponse:
        return cls(
            body=cast("str | JsonObject", structure.get("body", "")),
            status_code=cast("HTTPStatus | int | str", structure.get("statusCode", HTTPStatus.OK)),
            headers=cast("Mapping[str, str] | None", structure.get("headers")),
            mode=Response.Mode(cast("str", structure.get("_mode", "text"))),
        )


@dataclass(init=False)
class Response(BaseResponse):
    """Represents a `Mountebank 'is' response behavior <http://localhost:2525/docs/api/stubs>`_.

    :param body: Body text for response. Can be a string, or a JSON serialisable data structure.
    :param status_code: HTTP status code - prefer :class:`http.HTTPStatus` values.
    :param wait: `Add latency, in ms <http://localhost:2525/docs/api/behaviors#behavior-wait>`_.
    :param repeat: `Repeat this many times before moving on to next response
        <http://localhost:2525/docs/api/behaviors#behavior-repeat>`_.
    :param headers: Response HTTP headers
    :param mode: Mode - text or binary
    :param copy: Copy behavior
    :param decorate: `Decorate behavior <http://localhost:2525/docs/api/behaviors#behavior-decorate>`_.
    :param lookup: Lookup behavior
    :param shell_transform: shellTransform behavior
    :param http_response: HTTP Response Fields - use this **or** the body, status_code, headers and mode fields,
        not both.
    """

    class Mode(Enum):
        TEXT = "text"
        BINARY = "binary"

    wait: int | str | None = None
    repeat: int | None = None
    copy: list[Copy] | None = None
    decorate: str | None = None
    lookup: list[Lookup] | None = None
    shell_transform: str | Iterable[str] | None = None
    http_response: HttpResponse = field(default_factory=HttpResponse)

    def __init__(
        self,
        body: str | JsonObject = "",
        status_code: HTTPStatus | int | str = HTTPStatus.OK,
        wait: int | str | None = None,
        repeat: int | None = None,
        headers: Mapping[str, str] | None = None,
        mode: Response.Mode | None = None,
        copy: Copy | Iterable[Copy] | None = None,
        decorate: str | None = None,
        lookup: Lookup | Iterable[Lookup] | None = None,
        shell_transform: str | Iterable[str] | None = None,
        *,
        http_response: HttpResponse | None = None,
    ) -> None:
        self.http_response = http_response or HttpResponse(
            body=body, status_code=status_code, headers=headers, mode=mode
        )
        self.wait = wait
        self.repeat = repeat
        self.copy = self.one_or_many(copy)
        self.decorate = decorate
        self.lookup = self.one_or_many(lookup)
        self.shell_transform = shell_transform

    def as_structure(self) -> JsonObject:
        return {
            "is": (self.http_response.as_structure()),
            "_behaviors": self._behaviors_as_structure(),
        }

    def _behaviors_as_structure(self) -> JsonObject:
        behaviors: JsonObject = {}
        self.add_if_true(behaviors, "wait", self.wait)
        self.add_if_true(behaviors, "repeat", self.repeat)
        self.add_if_true(behaviors, "decorate", self.decorate)
        self.add_if_true(behaviors, "shellTransform", self.shell_transform)
        if self.copy:
            behaviors["copy"] = [c.as_structure() for c in self.copy]
        if self.lookup:
            behaviors["lookup"] = [lookup.as_structure() for lookup in self.lookup]
        return behaviors

    @classmethod
    def from_structure(cls, structure: JsonObject) -> Response:
        behaviors = cls.as_json_object(structure["_behaviors"]) if "_behaviors" in structure else {}
        return cls(
            http_response=HttpResponse.from_structure(cls.as_json_object(structure["is"])),
            wait=cast("int | str | None", behaviors.get("wait")),
            repeat=cast("int | None", behaviors.get("repeat")),
            decorate=cast("str | None", behaviors.get("decorate")),
            shell_transform=cast("str | None", behaviors.get("shellTransform")),
            copy=[Copy.from_structure(cls.as_json_object(c)) for c in cast("list[JsonValue]", behaviors["copy"])]
            if "copy" in behaviors
            else None,
            lookup=[
                Lookup.from_structure(cls.as_json_object(lk)) for lk in cast("list[JsonValue]", behaviors["lookup"])
            ]
            if "lookup" in behaviors
            else None,
        )

    @property
    def body(self) -> str | JsonObject | ET.Element | bytes:
        return self.http_response.body

    @property
    def status_code(self) -> HTTPStatus | int | str:
        return self.http_response.status_code

    @property
    def headers(self) -> Mapping[str, str] | None:
        return self.http_response.headers

    @property
    def mode(self) -> Response.Mode:
        return self.http_response.mode


@dataclass
class TcpResponse(BaseResponse):
    data: str

    def as_structure(self) -> JsonObject:
        return {"is": {"data": self.data}}

    @classmethod
    def from_structure(cls, structure: JsonObject) -> TcpResponse:
        return cls(data=cast("str", cls.as_json_object(structure["is"])["data"]))


@dataclass
class FaultResponse(BaseResponse):
    """Represents a `Mountebank fault response <https://localhost:2525/docs/api/faults>`_.

    :param fault: The fault to simulate.
    """

    class Fault(Enum):
        CONNECTION_RESET_BY_PEER = "CONNECTION_RESET_BY_PEER"
        RANDOM_DATA_THEN_CLOSE = "RANDOM_DATA_THEN_CLOSE"

    fault: FaultResponse.Fault

    def as_structure(self) -> JsonObject:
        return {"fault": self.fault.name}

    @classmethod
    def from_structure(cls, structure: JsonObject) -> FaultResponse:
        return cls(fault=cls.Fault(cast("str", structure["fault"])))


@dataclass
class Proxy(BaseResponse):
    """Represents a `Mountebank proxy <http://localhost:2525/docs/api/proxies>`_.

    :param to: The origin server, to which the request should proxy.
    """

    class Mode(Enum):
        """Defines the replay behavior of the proxy."""

        ONCE = "proxyOnce"
        ALWAYS = "proxyAlways"
        TRANSPARENT = "proxyTransparent"

    to: URL | str
    wait: int | None = None
    inject_headers: Mapping[str, str] | None = None
    mode: Proxy.Mode = Mode.ONCE
    predicate_generators: list[PredicateGenerator] = field(default_factory=list)
    decorate: str | None = None

    def as_structure(self) -> JsonObject:
        proxy: JsonObject = {"to": str(self.to), "mode": self.mode.value}
        self.add_if_true(proxy, "injectHeaders", self.inject_headers)
        self.add_if_true(proxy, "predicateGenerators", [pg.as_structure() for pg in self.predicate_generators])
        return {
            "proxy": proxy,
            "_behaviors": self._behaviors_as_structure(),
        }

    def _behaviors_as_structure(self) -> JsonObject:
        behaviors: JsonObject = {}
        self.add_if_true(behaviors, "wait", self.wait)
        self.add_if_true(behaviors, "decorate", self.decorate)
        return behaviors

    @classmethod
    def from_structure(cls, structure: JsonObject) -> Proxy:
        proxy_structure = cls.as_json_object(structure["proxy"])
        behaviors = cls.as_json_object(structure["_behaviors"]) if "_behaviors" in structure else {}
        return cls(
            to=URL(cast("str", proxy_structure["to"])),
            inject_headers=cast("Mapping[str, str] | None", proxy_structure.get("injectHeaders")),
            mode=Proxy.Mode(cast("str", proxy_structure["mode"])),
            predicate_generators=[
                PredicateGenerator.from_structure(cls.as_json_object(pg))
                for pg in cast("list[JsonValue]", proxy_structure.get("predicateGenerators", []))
            ],
            wait=cast("int | None", behaviors.get("wait")),
            decorate=cast("str | None", behaviors.get("decorate")),
        )


@dataclass
class PredicateGenerator(JsonSerializable):
    """Represents a `Mountebank predicate generator <https://localhost:2525/docs/api/proxies#proxy-predicate-generators>`_.

    :param path: Include the path in the generated predicate.
    """

    path: bool = False
    query: bool | JsonObject = False
    operator: Predicate.Operator = Predicate.Operator.EQUALS
    case_sensitive: bool = True

    def as_structure(self) -> JsonObject:
        matches: JsonObject = {}
        self.add_if_true(matches, "path", self.path)
        self.add_if_true(matches, "query", self.query)
        return {"caseSensitive": self.case_sensitive, "matches": matches}

    @classmethod
    def from_structure(cls, structure: JsonObject) -> PredicateGenerator:
        matches = cls.as_json_object(structure["matches"])
        return cls(
            path=cast("bool", matches.get("path", None)),
            query=cast("bool | JsonObject", matches.get("query", None)),
            operator=Predicate.Operator[cast("str", structure["operator"])]
            if "operator" in structure
            else Predicate.Operator.EQUALS,
            case_sensitive=cast("bool", structure.get("caseSensitive", False)),
        )


@dataclass
class InjectionResponse(BaseResponse, Injecting):
    """Represents a `Mountebank injection response <http://localhost:2525/docs/api/injection>`_.

    Injection requires Mountebank version 2.0 or higher.

    :param inject: JavaScript function to inject .
    """

    @classmethod
    def from_structure(cls, structure: JsonObject) -> InjectionResponse:
        return cls(inject=cast("str", structure["inject"]))
