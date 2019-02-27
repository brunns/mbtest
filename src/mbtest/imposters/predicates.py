# encoding=utf-8
from __future__ import unicode_literals, absolute_import, division, print_function
from abc import ABCMeta, abstractmethod
from enum import Enum

from six import add_metaclass

from mbtest.imposters.base import JsonSerializable


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
        self,
        path=None,
        method=None,
        query=None,
        body=None,
        headers=None,
        xpath=None,
        operator=Operator.EQUALS,
        case_sensitive=True,
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
        :param headers: Headers, keys and values.
        :type headers: dict(str, str)
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
        self.headers = headers
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
        self._set_if_in_dict(inner, "path", "path")
        self._set_if_in_dict(inner, "query", "query")
        self._set_if_in_dict(inner, "body", "body")
        self._set_if_in_dict(inner, "headers", "headers")
        if "method" in inner:
            self.method = Predicate.Method(inner["method"])

    def fields_as_structure(self):
        fields = {}
        self._add_if_true(fields, "path", self.path)
        self._add_if_true(fields, "query", self.query)
        self._add_if_true(fields, "body", self.body)
        self._add_if_true(fields, "headers", self.headers)
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


class TcpPredicate(BasePredicate):
    def __init__(self, data):
        self.data = data

    def as_structure(self):
        return {"contains": {"data": self.data}}
