# encoding=utf-8
import abc
from collections.abc import Sequence
from enum import Enum
from xml.etree import ElementTree as et  # nosec - We are creating, not parsing XML.

from mbtest.imposters.base import JsonSerializable


class Response(JsonSerializable):
    """Represents a Mountebank 'is' response behavior - see http://www.mbtest.org/docs/api/stubs"""

    class Mode(Enum):
        TEXT = "text"
        BINARY = "binary"

    def __init__(
        self, body="", status_code=200, wait=None, repeat=None, headers=None, mode=None, copy=None
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
        """
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

    @property
    def body(self):
        if isinstance(self._body, et.Element):
            return et.tostring(self._body, encoding="unicode")
        elif isinstance(self._body, bytes):
            return self._body.decode("utf-8")
        return self._body

    def as_structure(self):
        return {"is": (self._is_structure()), "_behaviors": self._behaviors_structure()}

    def _is_structure(self):
        is_structure = {"statusCode": self.status_code, "_mode": self.mode.value}
        if self.body:
            is_structure["body"] = self.body
        if self.headers:
            is_structure["headers"] = self.headers
        return is_structure

    def _behaviors_structure(self):
        behaviors = {}
        if self.wait:
            behaviors["wait"] = self.wait
        if self.repeat:
            behaviors["repeat"] = self.repeat
        if self.copy:
            behaviors["copy"] = [c.as_structure() for c in self.copy]
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


class Copy(JsonSerializable):
    """Represents a copy behavior - see http://www.mbtest.org/docs/api/behaviors#behavior-copy"""

    def __init__(self, from_, into, using):
        """
        :param from_: The name of the request field to copy from, or, if the request field is an object, then an object
        specifying the path to the request field.
        :type from_: str or dict(str, str)
        :param into: The token to replace in the response with the selected request value.
        :type into: str
        :param using: The configuration needed to select values from the response
        :type using: Using
        """
        self.from_ = from_
        self.into = into
        self.using = using

    def as_structure(self):
        return {"from": self.from_, "into": self.into, "using": self.using.as_structure()}


class Using(JsonSerializable, metaclass=abc.ABCMeta):
    class Method(Enum):
        REGEX = "regex"
        XPATH = "xpath"
        JSONPATH = "jsonpath"

    def __init__(self, method, selector):
        """
        :param method: The method used to select the value(s) from the request.
        :type method: Using.Method
        :param selector: The selector used to select the value(s) from the request.
        :type selector: str
        """
        self.method = method
        self.selector = selector

    def as_structure(self):
        return {"method": self.method.value, "selector": self.selector}


class UsingRegex(Using):
    def __init__(self, selector, ignore_case=False):
        """
        :param selector: The selector used to select the value(s) from the request.
        :type selector: str
        :param ignore_case: Uses a case-insensitive regular expression (For REGEX method)
        :type ignore_case: bool
        """
        super().__init__(Using.Method.REGEX, selector)
        self.ignore_case = ignore_case

    def as_structure(self):
        structure = super().as_structure()
        structure["options"] = {"ignoreCase": self.ignore_case}
        return structure


class TcpResponse(JsonSerializable):
    def __init__(self, data):
        self.data = data

    def as_structure(self):
        return {"is": {"data": self.data}}
