# encoding=utf-8
from __future__ import unicode_literals, absolute_import, division, print_function
from enum import Enum
from xml.etree import ElementTree as et  # nosec - We are creating, not parsing XML.

from six import PY3

from mbtest.imposters.base import JsonSerializable


class Response(JsonSerializable):
    """Represents a Mountebank 'is' response behavior - see http://www.mbtest.org/docs/api/stubs"""

    class Mode(Enum):
        TEXT = "text"
        BINARY = "binary"

    def __init__(self, body="", status_code=200, wait=None, repeat=None, headers=None, mode=None):
        """
        :param body: Body text for response. Can be a string, or a JSON serialisable data structure.
        :type body: str or dict or list or xml.etree.ElementTree.Element or bytes
        :param status_code: HTTP status code
        :type status_code: int
        :param wait: Add latency, in ms
        :type wait: int
        :param repeat: Repeat this many times before moving on to next response.
        :type repeat: int
        :param headers: Response HTTP headers
        :type headers: dict mapping from HTTP header name to header value
        """
        self._body = body
        self.status_code = status_code
        self.wait = wait
        self.repeat = repeat
        self.headers = headers
        self.mode = mode if isinstance(mode, Response.Mode) else Response.Mode(mode) if mode else Response.Mode.TEXT

    @property
    def body(self):
        if isinstance(self._body, et.Element):
            return et.tostring(self._body, encoding="unicode" if PY3 else "utf-8")
        elif isinstance(self._body, bytes):
            return self._body.decode("utf-8")
        return self._body

    def as_structure(self):
        inner = {"statusCode": self.status_code, "_mode": self.mode.value}
        if self.body:
            inner["body"] = self.body
        if self.headers:
            inner["headers"] = self.headers
        result = {"is": inner, "_behaviors": {}}
        if self.wait:
            result["_behaviors"]["wait"] = self.wait
        if self.repeat:
            result["_behaviors"]["repeat"] = self.repeat
        return result

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
