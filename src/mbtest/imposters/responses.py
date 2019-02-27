# encoding=utf-8
from __future__ import unicode_literals, absolute_import, division, print_function
from enum import Enum
from xml.etree import ElementTree as et  # nosec - We are creating, not parsing XML.

from six import PY3

from mbtest.imposters.base import JsonSerializable

if PY3:
    from collections.abc import Sequence
else:  # pragma: no cover
    from collections import Sequence


class Response(JsonSerializable):
    """Represents a Mountebank 'is' response behavior - see http://www.mbtest.org/docs/api/stubs"""

    class Mode(Enum):
        TEXT = "text"
        BINARY = "binary"

    def __init__(
        self,
        body="",
        status_code=200,
        wait=None,
        repeat=None,
        headers=None,
        mode=None,
        copy=None,
        decorate=None,
        lookup=None,
        shell_transform=None,
    ):
        """
        :param body: Body text for response. Can be a string, or a JSON serialisable data structure.
        :type body: str or dict or list or xml.etree.ElementTree.Element or bytes
        :param status_code: HTTP status code
        :type status_code: int or str
        :param wait: Add latency, in ms
        :type wait: int
        :param repeat: Repeat this many times before moving on to next response.
        :type repeat: int
        :param headers: Response HTTP headers
        :type headers: dict mapping from HTTP header name to header value
        :param mode: Mode - text or binary
        :type mode: Mode
        :param copy: Copy behavior
        :type copy: Copy or list(Copy)
        :param decorate: Decorate behavior
        :type decorate: str
        :param lookup: Lookup behavior
        :type lookup: Lookup or list(Lookup)
        :param shell_transform: shellTransform behavior
        :type shell_transform: str or list(str)
        """
        self._body = body
        self.status_code = status_code
        self.wait = wait
        self.repeat = repeat
        self.headers = headers
        self.mode = mode if isinstance(mode, Response.Mode) else Response.Mode(mode) if mode else Response.Mode.TEXT
        self.copy = copy if isinstance(copy, Sequence) else [copy] if copy else None
        self.decorate = decorate
        self.lookup = lookup if isinstance(lookup, Sequence) else [lookup] if lookup else None
        self.shell_transform = shell_transform

    @property
    def body(self):
        if isinstance(self._body, et.Element):
            return et.tostring(self._body, encoding="unicode" if PY3 else "utf-8")
        elif isinstance(self._body, bytes):
            return self._body.decode("utf-8")
        return self._body

    def as_structure(self):
        return {"is": (self._is_structure()), "_behaviors": self._behaviors_structure()}

    def _is_structure(self):
        is_structure = {"statusCode": self.status_code, "_mode": self.mode.value}
        self._add_if_true(is_structure, "body", self.body)
        self._add_if_true(is_structure, "headers", self.headers)
        return is_structure

    def _behaviors_structure(self):
        behaviors = {}
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
    def from_structure(structure):
        response = Response()
        response.fields_from_structure(structure)
        behaviors = structure.get("_behaviors")
        if not behaviors:
            return response
        if "wait" in behaviors:
            response.wait = behaviors["wait"]
        if "repeat" in behaviors:
            response.repeat = behaviors["repeat"]
        return response

    def fields_from_structure(self, structure):
        inner = structure["is"]
        if "body" in inner:
            self._body = inner["body"]
        if "headers" in inner:
            self.headers = inner["headers"]
        if "statusCode" in inner:
            self.status_code = inner["statusCode"]


class TcpResponse(JsonSerializable):
    def __init__(self, data):
        self.data = data

    def as_structure(self):
        return {"is": {"data": self.data}}
