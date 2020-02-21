# encoding=utf-8
from collections.abc import Sequence
from enum import Enum
from typing import Iterable, Mapping, Optional, Union
from xml.etree import ElementTree as et  # nosec - We are creating, not parsing XML.

from mbtest.imposters import Copy, Lookup
from mbtest.imposters.base import JsonSerializable, JsonStructure


class Response(JsonSerializable):
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
    """

    class Mode(Enum):
        TEXT = "text"
        BINARY = "binary"

    def __init__(
        self,
        body: str = "",
        status_code: Union[int, str] = 200,
        wait: Optional[Union[int, str]] = None,
        repeat: Optional[int] = None,
        headers: Optional[Mapping[str, str]] = None,
        mode: Optional[Mode] = None,
        copy: Optional[Copy] = None,
        decorate: Optional[str] = None,
        lookup: Optional[Lookup] = None,
        shell_transform: Optional[Union[str, Iterable[str]]] = None,
    ) -> None:
        self._body = body
        self.status_code = status_code
        self.wait = wait
        self.repeat = repeat
        self.headers = headers
        self.mode = (
            mode
            if isinstance(mode, Response.Mode)
            else Response.Mode(mode)
            if mode
            else Response.Mode.TEXT
        )
        self.copy = copy if isinstance(copy, Sequence) else [copy] if copy else None
        self.decorate = decorate
        self.lookup = lookup if isinstance(lookup, Sequence) else [lookup] if lookup else None
        self.shell_transform = shell_transform

    @property
    def body(self) -> str:
        if isinstance(self._body, et.Element):
            return et.tostring(self._body, encoding="unicode")
        elif isinstance(self._body, bytes):
            return self._body.decode("utf-8")
        return self._body

    def as_structure(self) -> JsonStructure:
        return {"is": (self._is_structure()), "_behaviors": self._behaviors_structure()}

    def _is_structure(self) -> JsonStructure:
        is_structure = {"statusCode": self.status_code, "_mode": self.mode.value}
        self._add_if_true(is_structure, "body", self.body)
        self._add_if_true(is_structure, "headers", self.headers)
        return is_structure

    def _behaviors_structure(self) -> JsonStructure:
        behaviors = {}  # type: JsonStructure
        self._add_if_true(behaviors, "wait", self.wait)
        self._add_if_true(behaviors, "repeat", self.repeat)
        self._add_if_true(behaviors, "decorate", self.decorate)
        self._add_if_true(behaviors, "shellTransform", self.shell_transform)
        if self.copy:
            behaviors["copy"] = [c.as_structure() for c in self.copy]
        if self.lookup:
            behaviors["lookup"] = [l.as_structure() for l in self.lookup]
        return behaviors

    @staticmethod
    def from_structure(structure: JsonStructure) -> "Response":
        response = Response()
        response._fields_from_structure(structure)
        behaviors = structure.get("_behaviors")
        response._set_if_in_dict(behaviors, "wait", "wait")
        response._set_if_in_dict(behaviors, "repeat", "repeat")
        response._set_if_in_dict(behaviors, "decorate", "decorate")
        response._set_if_in_dict(behaviors, "shellTransform", "shell_transform")
        if "copy" in behaviors:
            response.copy = [Copy.from_structure(c) for c in behaviors["copy"]]
        if "lookup" in behaviors:
            response.lookup = [Lookup.from_structure(l) for l in behaviors["lookup"]]
        return response

    def _fields_from_structure(self, structure: JsonStructure) -> None:
        inner = structure["is"]
        if "body" in inner:
            self._body = inner["body"]
        self.mode = Response.Mode(inner["_mode"])
        if "headers" in inner:
            self.headers = inner["headers"]
        if "statusCode" in inner:
            self.status_code = inner["statusCode"]


class TcpResponse(JsonSerializable):
    def __init__(self, data: str) -> None:
        self.data = data

    def as_structure(self) -> JsonStructure:
        return {"is": {"data": self.data}}

    @staticmethod
    def from_structure(structure: JsonStructure) -> "TcpResponse":
        return TcpResponse(data=structure["is"]["data"])
