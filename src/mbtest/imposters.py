import collections
import xml.etree.ElementTree as et  # nosec - We are creating, not parsing XML.
from abc import ABCMeta, abstractmethod
from enum import Enum

import six
from furl import furl
from six import add_metaclass


@add_metaclass(ABCMeta)
class JsonSerializable(object):
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

    def __init__(self, stubs, port=None, protocol=Protocol.HTTP, name=None, record_requests=False):
        """
        :param stubs: One or more Stubs.
        :type stubs: Stub or list(Stub)
        :param port: Port.
        :type port: int
        :param protocol: :Imposter.Protocol: to run on.
        :type protocol: Imposter.Protocol
        :param name: Impostor name - useful for interactive exploration of impostors on http://localhost:2525/impostors
        :type str
        :param record_requests: Record requests made against this impostor, so they can be asserted against later.
        :type record_requests: bool
        """
        self.stubs = stubs if isinstance(stubs, collections.Sequence) else [stubs]
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
            self.predicates = predicates if isinstance(predicates, collections.Sequence) else [predicates]
        else:
            self.predicates = [Predicate()]
        if responses:
            self.responses = responses if isinstance(responses, collections.Sequence) else [responses]
        else:
            self.responses = [Response()]

    def as_structure(self):
        return {
            "predicates": [predicate.as_structure() for predicate in self.predicates],
            "responses": [response.as_structure() for response in self.responses],
        }


@add_metaclass(ABCMeta)
class BasePredicate(JsonSerializable):
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
        if self.path:
            predicate["path"] = self.path
        if self.xpath:
            predicate["xpath"] = {"selector": self.xpath}
        return predicate

    def fields_as_structure(self):
        fields = {}
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
    def __init__(self, to):
        self.to = to

    def as_structure(self):
        return {"responses": [{"proxy": {"to": self.to}}]}


class Response(JsonSerializable):
    """Represents a Mountebank 'is' response behavior - see http://www.mbtest.org/docs/api/stubs"""

    def __init__(self, body="", status_code=200, wait=None, repeat=None):
        """
        :param body: Body text for response. Can be a string, or a JSON serialisable data structure.
        :type body: str or dict or list or xml.etree.ElementTree.Element
        :param status_code: HTTP status code
        :type status_code: int
        :param wait: Add latency, in ms
        :type wait: int
        :param repeat: Repeat this many times before moving on to next response.
        :type repeat: int
        """
        self._body = body
        self.status_code = status_code
        self.wait = wait
        self.repeat = repeat

    @property
    def body(self):
        if isinstance(self._body, et.Element):
            return et.tostring(self._body, encoding="unicode" if six.PY3 else "utf-8")
        return self._body

    def as_structure(self):
        inner = {"statusCode": self.status_code, "body": self.body}
        if self.body:
            inner["body"] = self.body
        result = {"is": inner, "_behaviors": {}}
        if self.wait:
            result["_behaviors"]["wait"] = self.wait
        if self.repeat:
            result["_behaviors"]["repeat"] = self.repeat
        return result


def smtp_imposter(name="smtp", record_requests=True):
    """Canned SMTP server impostor."""
    return Imposter([], 4525, name=name, protocol=Imposter.Protocol.SMTP, record_requests=record_requests)
