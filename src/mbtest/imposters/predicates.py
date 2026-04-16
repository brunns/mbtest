from __future__ import annotations

from abc import ABC
from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from typing import Any, cast

from mbtest.imposters.base import Injecting, JsonObject, JsonSerializable, JsonValue  # noqa: F401


@dataclass
class BasePredicate(JsonSerializable, ABC):
    @classmethod
    def from_structure(cls, structure: JsonObject) -> BasePredicate:  # noqa: C901
        if "and" in structure:
            return AndPredicate.from_structure(structure)
        if "or" in structure:
            return OrPredicate.from_structure(structure)
        if "not" in structure:
            return NotPredicate.from_structure(structure)
        if "contains" in structure and "data" in cls.as_json_object(structure["contains"]):
            return TcpPredicate.from_structure(structure)
        if "inject" in structure:
            return InjectionPredicate.from_structure(structure)
        if set(structure.keys()).intersection({o.value for o in Predicate.Operator}):  # pragma: no cover
            return Predicate.from_structure(structure)
        raise NotImplementedError  # pragma: no cover


@dataclass
class LogicallyCombinablePredicate(BasePredicate, ABC):
    def __and__(self, other: BasePredicate) -> AndPredicate:
        return AndPredicate(self, other)

    def __or__(self, other: BasePredicate) -> OrPredicate:
        return OrPredicate(self, other)

    def __invert__(self) -> NotPredicate:
        return NotPredicate(self)


@dataclass(init=False)
class Predicate(LogicallyCombinablePredicate):
    """Represents a `Mountebank predicate <http://localhost:2525/docs/api/predicates>`_.
    A predicate can be thought of as a trigger, which may or may not match a request.

    :param path: URL path.
    :param method: HTTP method.
    :param query: Query arguments, keys and values.
    :param body: Body text. Can be a string, or a JSON serialisable data structure.
    :param headers: Headers, keys and values.
    :param form: Form-encoded key-value pairs in the body.
    :param xpath: xpath query
    :param jsonpath: jsonpath query
    :param operator:
    :param case_sensitive:
    """

    class InvalidPredicateOperator(Exception):
        pass

    class Method(Enum):
        """Predicate HTTP method."""

        DELETE = "DELETE"
        GET = "GET"
        HEAD = "HEAD"
        POST = "POST"
        PUT = "PUT"
        PATCH = "PATCH"
        OPTIONS = "OPTIONS"

    class Operator(Enum):
        """`Predicate operator <http://localhost:2525/docs/api/predicates>`_."""

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

    path: str | None = None
    method: Predicate.Method | None = None
    query: Mapping[str, str | int | bool] | None = None
    body: str | JsonObject | None = None
    headers: Mapping[str, str] | None = None
    xpath: str | None = None
    jsonpath: str | None = None
    form: Mapping[str, str] | None = None
    operator: Predicate.Operator = Operator.EQUALS
    case_sensitive: bool = True

    def __init__(
        self,
        path: str | None = None,
        method: Predicate.Method | str | None = None,
        query: Mapping[str, str | int | bool] | None = None,
        body: str | JsonObject | None = None,
        headers: Mapping[str, str] | None = None,
        xpath: str | None = None,
        jsonpath: str | None = None,
        form: Mapping[str, str] | None = None,
        operator: Predicate.Operator | str = Operator.EQUALS,
        *,
        case_sensitive: bool = True,
    ) -> None:
        self.path = path
        self.method = method if isinstance(method, Predicate.Method) else Predicate.Method(method) if method else None
        self.query = query
        self.body = body
        self.headers = headers
        self.xpath = xpath
        self.jsonpath = jsonpath
        self.form = form
        self.operator = operator if isinstance(operator, Predicate.Operator) else Predicate.Operator(operator)
        self.case_sensitive = case_sensitive

    def as_structure(self) -> JsonObject:
        predicate = {
            self.operator.value: self.fields_as_structure(),
            "caseSensitive": self.case_sensitive,
        }
        if self.xpath:
            predicate["xpath"] = {"selector": self.xpath}
        if self.jsonpath:
            predicate["jsonpath"] = {"selector": self.jsonpath}
        return predicate

    @classmethod
    def from_structure(cls, structure: JsonObject) -> Predicate:
        operators = tuple(filter(Predicate.Operator.has_value, structure.keys()))
        if len(operators) != 1:
            msg = "Each predicate must define exactly one operator."
            raise Predicate.InvalidPredicateOperator(msg)
        operator = operators[0]
        inner = cls.as_json_object(structure[operator])
        return cls(
            operator=operator,
            case_sensitive=cast("bool", structure.get("caseSensitive", True)),
            path=cast("str | None", inner.get("path")),
            method=cast("str | None", inner.get("method")),
            query=cast("Mapping[str, str | int | bool] | None", inner.get("query")),
            body=cast("str | JsonObject | None", inner.get("body")),
            headers=cast("Mapping[str, str] | None", inner.get("headers")),
            form=cast("Mapping[str, str] | None", inner.get("form")),
            xpath=cast("str", cls.as_json_object(structure["xpath"])["selector"]) if "xpath" in structure else None,
            jsonpath=cast("str", cls.as_json_object(structure["jsonpath"])["selector"])
            if "jsonpath" in structure
            else None,
        )

    def fields_as_structure(self) -> dict[str, Any]:
        fields: dict[str, Any] = {}
        self.add_if_true(fields, "path", self.path)
        self.add_if_true(fields, "query", self.query)
        self.add_if_true(fields, "body", self.body)
        self.add_if_true(fields, "headers", self.headers)
        self.add_if_true(fields, "form", self.form)
        if self.method:
            fields["method"] = self.method.value
        return fields


@dataclass
class AndPredicate(LogicallyCombinablePredicate):
    left: BasePredicate
    right: BasePredicate

    def as_structure(self) -> JsonObject:
        return {"and": [self.left.as_structure(), self.right.as_structure()]}

    @classmethod
    def from_structure(cls, structure: JsonObject) -> AndPredicate:
        and_list = cast("list[JsonObject]", structure["and"])
        return cls(
            BasePredicate.from_structure(and_list[0]),
            BasePredicate.from_structure(and_list[1]),
        )


@dataclass
class OrPredicate(LogicallyCombinablePredicate):
    left: BasePredicate
    right: BasePredicate

    def as_structure(self) -> JsonObject:
        return {"or": [self.left.as_structure(), self.right.as_structure()]}

    @classmethod
    def from_structure(cls, structure: JsonObject) -> OrPredicate:
        or_list = cast("list[JsonObject]", structure["or"])
        return cls(
            BasePredicate.from_structure(or_list[0]),
            BasePredicate.from_structure(or_list[1]),
        )


@dataclass
class NotPredicate(LogicallyCombinablePredicate):
    inverted: BasePredicate

    def as_structure(self) -> JsonObject:
        return {"not": self.inverted.as_structure()}

    @classmethod
    def from_structure(cls, structure: JsonObject) -> NotPredicate:
        return cls(BasePredicate.from_structure(cls.as_json_object(structure["not"])))


@dataclass
class TcpPredicate(LogicallyCombinablePredicate):
    """Represents a `Mountebank TCP predicate <http://localhost:2525/docs/protocols/tcp>`_.
    A predicate can be thought of as a trigger, which may or may not match a request.

    :param data: Data to match the request.
    """

    data: str

    def as_structure(self) -> JsonObject:
        return {"contains": {"data": self.data}}

    @classmethod
    def from_structure(cls, structure: JsonObject) -> TcpPredicate:
        return cls(cast("str", cls.as_json_object(structure["contains"])["data"]))


@dataclass
class InjectionPredicate(BasePredicate, Injecting):
    """Represents a `Mountebank injection predicate <http://localhost:2525/docs/api/injection>`_.
    A predicate can be thought of as a trigger, which may or may not match a request.

    Injection requires Mountebank version 2.0 or higher.

    :param inject: JavaScript function to inject.
    """

    @classmethod
    def from_structure(cls, structure: JsonObject) -> InjectionPredicate:
        return cls(inject=cast("str", structure["inject"]))
