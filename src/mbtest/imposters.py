import collections
from abc import ABCMeta, abstractmethod
from enum import Enum

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
        :param predicates:
        :type predicates: Predicate or list(Predicate)
        :param responses:
        :type responses: Response or list(Response)
        """
        if responses:
            self.responses = responses if isinstance(responses, collections.Sequence) else [responses]
        else:
            self.responses = [Response()]
        if predicates:
            self.predicates = predicates if isinstance(predicates, collections.Sequence) else [predicates]
        else:
            self.predicates = [Predicate()]

    def as_structure(self):
        return {
            "responses": [response.as_structure() for response in self.responses],
            "predicates": [predicate.as_structure() for predicate in self.predicates],
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
    """See http://www.mbtest.org/docs/api/predicates"""

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
        self, path="/", method=Method.GET, query=None, body=None, operator=Operator.EQUALS, case_sensitive=True
    ):
        """
        :param path:
        :type path: str or furl.furl.furl
        :param method:
        :type method: Predicate.Method
        :param query:
        :type query: dict
        :param body:
        :type body: str
        :param operator:
        :type operator: Predicate.Operator
        :param case_sensitive:
        :type case_sensitive: bool
        """
        self.path = path
        self.method = method if isinstance(method, Predicate.Method) else Predicate.Method(method)
        self.query = query
        self.body = body
        self.operator = operator if isinstance(operator, Predicate.Operator) else Predicate.Operator(operator)
        self.case_sensitive = case_sensitive

    def as_structure(self):
        fields = {"path": self.path, "method": self.method.value}
        if self.query:
            fields["query"] = self.query
        if self.body:
            fields["body"] = self.body
        return {self.operator.value: fields, "caseSensitive": self.case_sensitive}


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
    """TODO"""
    def __init__(self, body="", status_code=200, wait=None, repeat=None):
        """
        :param body:
        :type body: str
        :param status_code:
        :type status_code: int
        :param wait:
        :type wait: bool
        :param repeat:
        :type repeat: int
        """
        self.body = body
        self.status_code = status_code
        self.wait = wait
        self.repeat = repeat

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


def smtp_imposter(record_requests=True):
    """TODO"""
    return Imposter([], 4525, name="smtp", protocol=Imposter.Protocol.SMTP, record_requests=record_requests)
