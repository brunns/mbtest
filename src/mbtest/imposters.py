# encoding=utf-8
import xml.etree.ElementTree as et  # nosec - We are creating, not parsing XML.
from abc import ABCMeta, abstractmethod
from collections.abc import Sequence
from enum import Enum

from furl import furl


class JsonSerializable(object, metaclass=ABCMeta):
    @abstractmethod
    def as_structure(self):  # pragma: no cover
        """
        :returns Structure suitable for JSON serialisation.
        :rtype: dict
        """
        raise NotImplementedError()


class Imposter(JsonSerializable):
    """Represents a Mountebank imposter - see http://www.mbtest.org/docs/api/mocks.
    Think of an imposter as a mock website, running a protocol, on a specific port.
    The specific behaviors require

    Pass to an :mbtest.server.mock_server:.
    """

    class Protocol(Enum):
        HTTP = "http"
        HTTPS = "https"
        SMTP = "smtp"

    def __init__(self, stubs, port=None, protocol=Protocol.HTTP, name=None, record_requests=True):
        """
        :param stubs: One or more Stubs.
        :type stubs: Stub or list(Stub)
        :param port: Port.
        :type port: int
        :param protocol: :Imposter.Protocol: to run on.
        :type protocol: Imposter.Protocol
        :param name: Impostor name - useful for interactive exploration of impostors on http://localhost:2525/impostors
        :type name: str
        :param record_requests: Record requests made against this impostor, so they can be asserted against later.
        :type record_requests: bool
        """
        stubs = stubs if isinstance(stubs, Sequence) else [stubs]
        # For backwards compatability where previously a proxy may have been used directly as a stub.
        self.stubs = [Stub(responses=stub) if isinstance(stub, Proxy) else stub for stub in stubs]
        self.port = port
        self.protocol = protocol if isinstance(protocol, Imposter.Protocol) else Imposter.Protocol(protocol)
        self.name = name
        self.record_requests = record_requests

    def as_structure(self):
        structure = {"protocol": self.protocol.value, "recordRequests": self.record_requests}
        if self.port:
            structure["port"] = self.port
        if self.name:
            structure["name"] = self.name
        if self.stubs:
            structure["stubs"] = [stub.as_structure() for stub in self.stubs]
        return structure

    @staticmethod
    def from_structure(structure):
        imposter = Imposter([Stub.from_structure(stub) for stub in structure["stubs"]])
        if "port" in structure:
            imposter.port = structure["port"]
        if "protocol" in structure:
            protocol = structure["protocol"]
            imposter.protocol = protocol if isinstance(protocol, Imposter.Protocol) else Imposter.Protocol(protocol)
        if "recordRequests" in structure:
            imposter.record_requests = structure["recordRequests"]
        if "name" in structure:
            imposter.name = structure["name"]
        return imposter

    @property
    def host(self):
        return "localhost"

    @property
    def url(self):
        return furl().set(scheme=self.protocol.value, host=self.host, port=self.port).url


class Stub(JsonSerializable):
    """Represents a Mountebank stub - see http://www.mbtest.org/docs/api/stubs.
    Think of a stub as a behavior, triggered by a matching predicate.
    """

    def __init__(self, predicates=None, responses=None):
        """
        :param predicates: Trigger this stub if one of these predicates matches the request
        :type predicates: Predicate or list(Predicate)
        :param responses: Use these response behaviors (in order)
        :type responses: Response or list(Response)
        """
        if predicates:
            self.predicates = predicates if isinstance(predicates, Sequence) else [predicates]
        else:
            self.predicates = [Predicate()]
        if responses:
            self.responses = responses if isinstance(responses, Sequence) else [responses]
        else:
            self.responses = [Response()]

    def as_structure(self):
        return {
            "predicates": [predicate.as_structure() for predicate in self.predicates],
            "responses": [response.as_structure() for response in self.responses],
        }

    @staticmethod
    def from_structure(structure):
        responses = []
        for response in structure.get("responses", ()):
            if "proxy" in response:
                responses.append(Proxy.from_structure(response))
            else:
                responses.append(Response.from_structure(response))
        return Stub([Predicate.from_structure(predicate) for predicate in structure.get("predicates", ())], responses)


class BasePredicate(JsonSerializable, metaclass=ABCMeta):
    @abstractmethod
    def as_structure(self):  # pragma: no cover
        raise NotImplementedError()

    def __and__(self, other):
        return AndPredicate(self, other)

    def __or__(self, other):
        return OrPredicate(self, other)


class Predicate(BasePredicate):
    """"Represents a Mountebank predicate - see http://www.mbtest.org/docs/api/predicates
    A predicate can be thought of as a trigger, which may or may not match a request."""

    class InvalidPredicateOperator(Exception):
        pass

    class Method(Enum):
        GET = "GET"
        PUT = "PUT"
        POST = "POST"
        DELETE = "DELETE"

    class Operator(Enum):
        EQUALS = "equals"
        DEEP_EQUALS = "deepEquals"
        CONTAINS = "contains"
        STARTS_WITH = "startsWith"
        ENDS_WITH = "endsWith"
        MATCHES = "matches"
        EXISTS = "exists"

        @classmethod
        def has_value(cls, value):
            return any(value == item.value for item in cls)

    def __init__(
        self, path=None, method=None, query=None, body=None, xpath=None, operator=Operator.EQUALS, case_sensitive=True
    ):
        """
        :param path: URL path.
        :type path: str or furl.furl.furl
        :param method: HTTP method.
        :type method: Predicate.Method
        :param query: Query arguments, keys and values.
        :type query: dict(str, str)
        :param body: Body text. Can be a string, or a JSON serialisable data structure.
        :type body: str or dict or list
        :param xpath: xpath query
        :type xpath: str
        :param operator:
        :type operator: Predicate.Operator
        :param case_sensitive:
        :type case_sensitive: bool
        """
        self.path = path
        self.method = method if isinstance(method, Predicate.Method) else Predicate.Method(method) if method else None
        self.query = query
        self.body = body
        self.xpath = xpath
        self.operator = operator if isinstance(operator, Predicate.Operator) else Predicate.Operator(operator)
        self.case_sensitive = case_sensitive

    def as_structure(self):
        predicate = {self.operator.value: self.fields_as_structure(), "caseSensitive": self.case_sensitive}
        if self.xpath:
            predicate["xpath"] = {"selector": self.xpath}
        return predicate

    @staticmethod
    def from_structure(structure):
        operators = tuple(filter(lambda operator: Predicate.Operator.has_value(operator), structure.keys()))
        if len(operators) != 1:
            raise Predicate.InvalidPredicateOperator("Each predicate must define exactly one operator.")
        operator = operators[0]
        predicate = Predicate(operator=operator, case_sensitive=structure.get("caseSensitive", True))
        predicate.fields_from_structure(structure[operator])
        if "xpath" in structure:
            predicate.xpath = structure["xpath"]["selector"]
        return predicate

    def fields_from_structure(self, inner):
        if "path" in inner:
            self.path = inner["path"]
        if "query" in inner:
            self.query = inner["query"]
        if "body" in inner:
            self.body = inner["body"]
        if "method" in inner:
            self.method = Predicate.Method(inner["method"])

    def fields_as_structure(self):
        fields = {}
        if self.path:
            fields["path"] = self.path
        if self.query:
            fields["query"] = self.query
        if self.body:
            fields["body"] = self.body
        if self.method:
            fields["method"] = self.method.value
        return fields


class AndPredicate(BasePredicate):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def as_structure(self):
        return {"and": [self.left.as_structure(), self.right.as_structure()]}


class OrPredicate(BasePredicate):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def as_structure(self):
        return {"or": [self.left.as_structure(), self.right.as_structure()]}


class Proxy(JsonSerializable):
    def __init__(self, to, wait=None):
        self.to = to
        self.wait = wait

    def as_structure(self):
        response = {"proxy": {"to": self.to}}
        if self.wait:
            response["_behaviors"] = {"wait": self.wait}
        return response

    @staticmethod
    def from_structure(structure):
        proxy_structure = structure["proxy"]
        proxy = Proxy(proxy_structure["to"])
        wait = structure.get("_behaviors", {}).get("wait")
        if wait:
            proxy.wait = wait
        return proxy


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
            return et.tostring(self._body, encoding="unicode")
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


def smtp_imposter(name="smtp", record_requests=True):
    """Canned SMTP server impostor."""
    return Imposter([], 4525, protocol=Imposter.Protocol.SMTP, name=name, record_requests=record_requests)
