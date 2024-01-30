# encoding=utf-8
from abc import ABC
from collections.abc import Sequence
from enum import Enum
from typing import Iterable, Mapping, MutableMapping, Optional, Union
from xml.etree import ElementTree as et  # nosec - We are creating, not parsing XML.

from furl import furl
from imurl.url import URL

from mbtest.imposters.base import Injecting, JsonSerializable, JsonStructure
from mbtest.imposters.behaviors import Copy, Lookup
from mbtest.imposters.predicates import Predicate


class BaseResponse(JsonSerializable, ABC):
    @classmethod
    def from_structure(cls, structure: JsonStructure) -> "BaseResponse":  # noqa: C901
        if "is" in structure and "_behaviors" in structure:
            return Response.from_structure(structure)
        elif "is" in structure and "data" in structure["is"]:
            return TcpResponse.from_structure(structure)
        elif "proxy" in structure:
            return Proxy.from_structure(structure)
        elif "inject" in structure:
            return InjectionResponse.from_structure(structure)
        elif "fault" in structure:
            return FaultResponse.from_structure(structure)
        raise NotImplementedError()  # pragma: no cover


class HttpResponse(JsonSerializable):
    """Represents a `Mountebank HTTP response <http://www.mbtest.org/docs/protocols/http>`_.

    :param body: Body text for response. Can be a string, or a JSON serialisable data structure.
    :param status_code: HTTP status code
    :param headers: Response HTTP headers
    :param mode: Mode - text or binary

    """

    def __init__(
        self,
        body: Union[str, JsonStructure] = "",
        status_code: Union[int, str] = 200,
        headers: Optional[Mapping[str, str]] = None,
        mode: Optional["Response.Mode"] = None,
    ) -> None:
        super().__init__()
        self._body = body
        self.status_code = status_code
        self.headers = headers
        self.mode = (
            mode
            if isinstance(mode, Response.Mode)
            else Response.Mode(mode) if mode else Response.Mode.TEXT
        )

    @property
    def body(self) -> str:
        if isinstance(self._body, et.Element):
            return et.tostring(self._body, encoding="unicode")
        elif isinstance(self._body, bytes):
            return self._body.decode("utf-8")
        return self._body

    def as_structure(self) -> JsonStructure:
        is_structure = {"statusCode": self.status_code, "_mode": self.mode.value}
        self.add_if_true(is_structure, "body", self.body)
        self.add_if_true(is_structure, "headers", self.headers)
        return is_structure

    @classmethod
    def from_structure(cls, inner: JsonStructure) -> "HttpResponse":
        response = cls()
        response.set_if_in_dict(inner, "body", "_body")
        response.mode = Response.Mode(inner.get("_mode", "text"))
        response.set_if_in_dict(inner, "headers", "headers")
        response.set_if_in_dict(inner, "statusCode", "status_code")
        return response


class Response(BaseResponse):
    """Represents a `Mountebank 'is' response behavior <http://www.mbtest.org/docs/api/stubs>`_.

    :param body: Body text for response. Can be a string, or a JSON serialisable data structure.
    :param status_code: HTTP status code
    :param wait: `Add latency, in ms <http://www.mbtest.org/docs/api/behaviors#behavior-wait>`_.
    :param repeat: `Repeat this many times before moving on to next response
        <http://www.mbtest.org/docs/api/behaviors#behavior-repeat>`_.
    :param headers: Response HTTP headers
    :param mode: Mode - text or binary
    :param copy: Copy behavior
    :param decorate: `Decorate behavior <http://www.mbtest.org/docs/api/behaviors#behavior-decorate>`_.
    :param lookup: Lookup behavior
    :param shell_transform: shellTransform behavior
    :param http_response: HTTP Response Fields - use this **or** the body, status_code, headers and mode fields, not both.
    """

    class Mode(Enum):
        TEXT = "text"
        BINARY = "binary"

    def __init__(
        self,
        body: Union[str, JsonStructure] = "",
        status_code: Union[int, str] = 200,
        wait: Optional[Union[int, str]] = None,
        repeat: Optional[int] = None,
        headers: Optional[Mapping[str, str]] = None,
        mode: Optional[Mode] = None,
        copy: Optional[Copy] = None,
        decorate: Optional[str] = None,
        lookup: Optional[Lookup] = None,
        shell_transform: Optional[Union[str, Iterable[str]]] = None,
        *,
        http_response: Optional[HttpResponse] = None,
    ) -> None:
        self.http_response = http_response or HttpResponse(
            body=body, status_code=status_code, headers=headers, mode=mode
        )
        # TODO: Deprecate HttpResponse arguments
        self.wait = wait
        self.repeat = repeat
        self.copy = copy if isinstance(copy, Sequence) else [copy] if copy else None
        self.decorate = decorate
        self.lookup = lookup if isinstance(lookup, Sequence) else [lookup] if lookup else None
        self.shell_transform = shell_transform

    def as_structure(self) -> JsonStructure:
        return {
            "is": (self.http_response.as_structure()),
            "_behaviors": self._behaviors_as_structure(),
        }

    def _behaviors_as_structure(self) -> JsonStructure:
        behaviors: JsonStructure = {}
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
    def from_structure(cls, structure: JsonStructure) -> "Response":
        response = cls()
        response.http_response = HttpResponse.from_structure(structure["is"])
        behaviors = structure.get("_behaviors", {})
        response.set_if_in_dict(behaviors, "wait", "wait")
        response.set_if_in_dict(behaviors, "repeat", "repeat")
        response.set_if_in_dict(behaviors, "decorate", "decorate")
        response.set_if_in_dict(behaviors, "shellTransform", "shell_transform")
        if "copy" in behaviors:
            response.copy = [Copy.from_structure(c) for c in behaviors["copy"]]
        if "lookup" in behaviors:
            response.lookup = [Lookup.from_structure(lookup) for lookup in behaviors["lookup"]]
        return response

    @property
    def body(self):
        return self.http_response.body

    @property
    def status_code(self):
        return self.http_response.status_code

    @property
    def headers(self):
        return self.http_response.headers

    @property
    def mode(self):
        return self.http_response.mode


class TcpResponse(BaseResponse):
    def __init__(self, data: str) -> None:
        self.data = data

    def as_structure(self) -> JsonStructure:
        return {"is": {"data": self.data}}

    @classmethod
    def from_structure(cls, structure: JsonStructure) -> "TcpResponse":
        return cls(data=structure["is"]["data"])


class FaultResponse(BaseResponse):
    """Represents a `Mountebank fault response <https://www.mbtest.org/docs/api/faults>`_.

    :param fault: The fault to simulate.
    """

    class Fault(Enum):
        CONNECTION_RESET_BY_PEER = "CONNECTION_RESET_BY_PEER"
        RANDOM_DATA_THEN_CLOSE = "RANDOM_DATA_THEN_CLOSE"

    def __init__(self, fault: Fault) -> None:
        self.fault = fault

    def as_structure(self) -> JsonStructure:
        return {"fault": self.fault.name}

    @classmethod
    def from_structure(cls, structure: JsonStructure) -> "FaultResponse":
        fault = cls.Fault(structure["fault"])
        return cls(fault=fault)


class Proxy(BaseResponse):
    """Represents a `Mountebank proxy <http://www.mbtest.org/docs/api/proxies>`_.

    :param to: The origin server, to which the request should proxy.
    """

    class Mode(Enum):
        """Defines the replay behavior of the proxy."""

        ONCE = "proxyOnce"
        ALWAYS = "proxyAlways"
        TRANSPARENT = "proxyTransparent"

    def __init__(
        self,
        to: Union[furl, URL, str],
        wait: Optional[int] = None,
        inject_headers: Optional[Mapping[str, str]] = None,
        mode: "Proxy.Mode" = Mode.ONCE,
        predicate_generators: Optional[Iterable["PredicateGenerator"]] = None,
        decorate: Optional[str] = None,
    ) -> None:
        self.to = to
        self.wait = wait
        self.inject_headers = inject_headers
        self.mode = mode
        self.predicate_generators = predicate_generators if predicate_generators is not None else []
        self.decorate = decorate

    def as_structure(self) -> JsonStructure:
        proxy = {
            "to": furl(self.to).url,
            "mode": self.mode.value,
        }
        self.add_if_true(proxy, "injectHeaders", self.inject_headers)
        self.add_if_true(
            proxy, "predicateGenerators", [pg.as_structure() for pg in self.predicate_generators]
        )
        return {
            "proxy": proxy,
            "_behaviors": self._behaviors_as_structure(),
        }

    def _behaviors_as_structure(self) -> JsonStructure:
        behaviors: JsonStructure = {}
        self.add_if_true(behaviors, "wait", self.wait)
        self.add_if_true(behaviors, "decorate", self.decorate)
        return behaviors

    @classmethod
    def from_structure(cls, structure: JsonStructure) -> "Proxy":
        proxy_structure = structure["proxy"]
        proxy = cls(
            to=furl(proxy_structure["to"]),
            inject_headers=(
                proxy_structure["injectHeaders"] if "injectHeaders" in proxy_structure else None
            ),
            mode=Proxy.Mode(proxy_structure["mode"]),
            predicate_generators=(
                [
                    PredicateGenerator.from_structure(pg)
                    for pg in proxy_structure["predicateGenerators"]
                ]
                if "predicateGenerators" in proxy_structure
                else None
            ),
        )
        behaviors = structure.get("_behaviors", {})
        proxy.set_if_in_dict(behaviors, "wait", "wait")
        proxy.set_if_in_dict(behaviors, "decorate", "decorate")
        return proxy


class PredicateGenerator(JsonSerializable):
    """Represents a `Mountebank predicate generator <https://www.mbtest.org/docs/api/proxies#proxy-predicate-generators>`_.

    :param path: Include the path in the generated predicate.
    """

    def __init__(
        self,
        path: bool = False,
        query: Union[bool, Mapping[str, str]] = False,
        # method: bool = False,
        # body: bool = False,
        # headers: Union[bool, Mapping[str, str]] = False,
        operator: Predicate.Operator = Predicate.Operator.EQUALS,
        case_sensitive: bool = True,
        # ignore_query: bool = False,
    ):
        self.path = path
        self.query = query
        self.operator = operator
        self.case_sensitive = case_sensitive

    def as_structure(self) -> JsonStructure:
        matches: MutableMapping[str, str] = {}
        self.add_if_true(matches, "path", self.path)
        self.add_if_true(matches, "query", self.query)
        predicate = {"caseSensitive": self.case_sensitive, "matches": matches}
        return predicate

    @classmethod
    def from_structure(cls, structure: JsonStructure) -> "PredicateGenerator":
        path = structure["matches"].get("path", None)
        query = structure["matches"].get("query", None)
        operator = (
            Predicate.Operator[structure["operator"]]
            if "operator" in structure
            else Predicate.Operator.EQUALS
        )
        case_sensitive = structure.get("caseSensitive", False)
        return cls(path=path, query=query, operator=operator, case_sensitive=case_sensitive)


class InjectionResponse(BaseResponse, Injecting):
    """Represents a `Mountebank injection response <http://www.mbtest.org/docs/api/injection>`_.

    Injection requires Mountebank version 2.0 or higher.

    :param inject: JavaScript function to inject .
    """

    @classmethod
    def from_structure(cls, structure: JsonStructure) -> "InjectionResponse":
        return cls(inject=structure["inject"])
