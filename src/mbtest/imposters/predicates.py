# encoding=utf-8
from abc import ABCMeta
from enum import Enum
from typing import Mapping, Optional, Union

from furl import furl
from mbtest.imposters.base import JsonSerializable, JsonStructure


class BasePredicate(JsonSerializable, metaclass=ABCMeta):
    def __and__(self, other: "BasePredicate") -> "AndPredicate":
        return AndPredicate(self, other)

    def __or__(self, other: "BasePredicate") -> "OrPredicate":
        return OrPredicate(self, other)

    @staticmethod
    def from_structure(structure: JsonStructure) -> "BasePredicate":
        if "and" in structure:
            return AndPredicate.from_structure(structure)
        elif "or" in structure:
            return OrPredicate.from_structure(structure)
        elif "contains" in structure and "data" in structure["contains"]:
            return TcpPredicate.from_structure(structure)
        elif set(structure.keys()).intersection(
            {o.value for o in Predicate.Operator}
        ):  # pragma: no cover
            return Predicate.from_structure(structure)
        raise NotImplementedError()  # pragma: no cover


class Predicate(BasePredicate):
    """"Represents a Mountebank predicate - see http://www.mbtest.org/docs/api/predicates
    A predicate can be thought of as a trigger, which may or may not match a request."""

    class InvalidPredicateOperator(Exception):
        pass

    class Method(Enum):
        DELETE = "DELETE"
        GET = "GET"
        HEAD = "HEAD"
        POST = "POST"
        PUT = "PUT"

    class Operator(Enum):
        EQUALS = "equals"
        DEEP_EQUALS = "deepEquals"
        CONTAINS = "contains"
        STARTS_WITH = "startsWith"
        ENDS_WITH = "endsWith"
        MATCHES = "matches"
        EXISTS = "exists"

        @classmethod
        def has_value(cls, name: str) -> bool:
            return any(name == item.value for item in cls)

    def __init__(
        self,
        path: Optional[Union[str, furl]] = None,
        method: Optional[Method] = None,
        query: Optional[Mapping[str, Union[str, int, bool]]] = None,
        body: Optional[str] = None,
        headers: Optional[Mapping[str, str]] = None,
        xpath: Optional[str] = None,
        operator: Operator = Operator.EQUALS,
        case_sensitive: bool = True,
    ) -> None:
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
        self.method = (
            method
            if isinstance(method, Predicate.Method)
            else Predicate.Method(method)
            if method
            else None
        )
        self.query = query
        self.body = body
        self.headers = headers
        self.xpath = xpath
        self.operator = (
            operator if isinstance(operator, Predicate.Operator) else Predicate.Operator(operator)
        )
        self.case_sensitive = case_sensitive

    def as_structure(self) -> JsonStructure:
        predicate = {
            self.operator.value: self.fields_as_structure(),
            "caseSensitive": self.case_sensitive,
        }
        if self.xpath:
            predicate["xpath"] = {"selector": self.xpath}
        return predicate

    @staticmethod
    def from_structure(structure: JsonStructure) -> "Predicate":
        operators = tuple(filter(Predicate.Operator.has_value, structure.keys()))
        if len(operators) != 1:
            raise Predicate.InvalidPredicateOperator(
                "Each predicate must define exactly one operator."
            )
        operator = operators[0]
        predicate = Predicate(
            operator=operator, case_sensitive=structure.get("caseSensitive", True)
        )
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
    def __init__(self, left: BasePredicate, right: BasePredicate) -> None:
        self.left = left
        self.right = right

    def as_structure(self) -> JsonStructure:
        return {"and": [self.left.as_structure(), self.right.as_structure()]}

    @staticmethod
    def from_structure(structure: JsonStructure) -> "AndPredicate":
        return AndPredicate(
            BasePredicate.from_structure(structure["and"][0]),
            BasePredicate.from_structure(structure["and"][1]),
        )


class OrPredicate(BasePredicate):
    def __init__(self, left: BasePredicate, right: BasePredicate) -> None:
        self.left = left
        self.right = right

    def as_structure(self) -> JsonStructure:
        return {"or": [self.left.as_structure(), self.right.as_structure()]}

    @staticmethod
    def from_structure(structure: JsonStructure) -> "OrPredicate":
        return OrPredicate(
            BasePredicate.from_structure(structure["or"][0]),
            BasePredicate.from_structure(structure["or"][1]),
        )


class TcpPredicate(BasePredicate):
    def __init__(self, data: str) -> None:
        self.data = data

    def as_structure(self) -> JsonStructure:
        return {"contains": {"data": self.data}}

    @staticmethod
    def from_structure(structure: JsonStructure) -> "TcpPredicate":
        return TcpPredicate(structure["contains"]["data"])
