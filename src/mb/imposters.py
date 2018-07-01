import collections
from abc import ABCMeta, abstractmethod

from furl import furl


class JsonSerializable(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def as_structure(self):  # pragma: no cover
        raise NotImplementedError()


class Imposter(JsonSerializable):
    """See http://www.mbtest.org/docs/api/mocks"""

    def __init__(self, stubs, port=None, protocol="http", name=None, record_requests=False):
        self.stubs = stubs if isinstance(stubs, collections.Sequence) else [stubs]
        self.port = port
        self.protocol = protocol
        self.name = name
        self.record_requests = record_requests

    def as_structure(self):
        structure = {"protocol": self.protocol, "recordRequests": self.record_requests}
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
        return furl().set(scheme=self.protocol, host=self.host, port=self.port).url


class Stub(JsonSerializable):
    """See http://www.mbtest.org/docs/api/stubs"""

    def __init__(self, predicates=None, responses=None):
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

    def __init__(self, path="/", method="GET", query=None, body=None, operator="equals", case_sensitive=True):
        self.path = path
        self.method = method
        self.query = query
        self.body = body
        self.operator = operator
        self.case_sensitive = case_sensitive

    def as_structure(self):
        fields = {"path": self.path, "method": self.method}
        if self.query:
            fields["query"] = self.query
        if self.body:
            fields["body"] = self.body
        return {self.operator: fields, "caseSensitive": self.case_sensitive}


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
    def __init__(self, body="", status_code=200, wait=None, repeat=None):
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
    return Imposter([], 4525, name="smtp", protocol="smtp", record_requests=record_requests)
