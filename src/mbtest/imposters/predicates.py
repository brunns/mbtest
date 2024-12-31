from abc import ABC
from collections.abc import Mapping
from enum import Enum
from typing import Optional, Union

from mbtest.imposters.base import Injecting, JsonSerializable, JsonStructure


class BasePredicate(JsonSerializable, ABC):
    @classmethod
    def from_structure(cls, structure: JsonStructure) -> "BasePredicate":  # noqa: C901
        if "and" in structure:
            return AndPredicate.from_structure(structure)
        if "or" in structure:
            return OrPredicate.from_structure(structure)
        if "not" in structure:
            return NotPredicate.from_structure(structure)
        if "contains" in structure and "data" in structure["contains"]:
            return TcpPredicate.from_structure(structure)
        if "inject" in structure:
            return InjectionPredicate.from_structure(structure)
        if set(structure.keys()).intersection({o.value for o in Predicate.Operator}):  # pragma: no cover
            return Predicate.from_structure(structure)
        raise NotImplementedError  # pragma: no cover


class LogicallyCombinablePredicate(BasePredicate, ABC):
    def __and__(self, other: "BasePredicate") -> "AndPredicate":
        return AndPredicate(self, other)

    def __or__(self, other: "BasePredicate") -> "OrPredicate":
        return OrPredicate(self, other)

    def __invert__(self) -> "NotPredicate":
        return NotPredicate(self)


class Predicate(LogicallyCombinablePredicate):
    """Represents a `Mountebank predicate <http://www.mbtest.org/docs/api/predicates>`_.
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
        """`Predicate operator <http://www.mbtest.org/docs/api/predicates>`_."""

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
        path: Optional[str] = None,
        method: Optional[Union[Method, str]] = None,
        query: Optional[Mapping[str, Union[str, int, bool]]] = None,
        body: Optional[Union[str, JsonStructure]] = None,
        headers: Optional[Mapping[str, str]] = None,
        xpath: Optional[str] = None,
        jsonpath: Optional[str] = None,
        form: Optional[Mapping[str, str]] = None,
        operator: Union[Operator, str] = Operator.EQUALS,
        case_sensitive: bool = True,  # noqa: FBT001,FBT002
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

    def as_structure(self) -> JsonStructure:
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
    def from_structure(cls, structure: JsonStructure) -> "Predicate":
        operators = tuple(filter(Predicate.Operator.has_value, structure.keys()))
        if len(operators) != 1:
            msg = "Each predicate must define exactly one operator."
            raise Predicate.InvalidPredicateOperator(msg)
        operator = operators[0]
        predicate = cls(operator=operator, case_sensitive=structure.get("caseSensitive", True))
        predicate.fields_from_structure(structure[operator])
        if "xpath" in structure:
            predicate.xpath = structure["xpath"]["selector"]
        if "jsonpath" in structure:
            predicate.jsonpath = structure["jsonpath"]["selector"]
        return predicate

    def fields_from_structure(self, inner):
        self.set_if_in_dict(inner, "path", "path")
        self.set_if_in_dict(inner, "query", "query")
        self.set_if_in_dict(inner, "body", "body")
        self.set_if_in_dict(inner, "headers", "headers")
        self.set_if_in_dict(inner, "form", "form")
        if "method" in inner:
            self.method = Predicate.Method(inner["method"])

    def fields_as_structure(self):
        fields = {}
        self.add_if_true(fields, "path", self.path)
        self.add_if_true(fields, "query", self.query)
        self.add_if_true(fields, "body", self.body)
        self.add_if_true(fields, "headers", self.headers)
        self.add_if_true(fields, "form", self.form)
        if self.method:
            fields["method"] = self.method.value
        return fields


class AndPredicate(LogicallyCombinablePredicate):
    def __init__(self, left: BasePredicate, right: BasePredicate) -> None:
        self.left = left
        self.right = right

    def as_structure(self) -> JsonStructure:
        return {"and": [self.left.as_structure(), self.right.as_structure()]}

    @classmethod
    def from_structure(cls, structure: JsonStructure) -> "AndPredicate":
        return cls(
            BasePredicate.from_structure(structure["and"][0]),
            BasePredicate.from_structure(structure["and"][1]),
        )


class OrPredicate(LogicallyCombinablePredicate):
    def __init__(self, left: BasePredicate, right: BasePredicate) -> None:
        self.left = left
        self.right = right

    def as_structure(self) -> JsonStructure:
        return {"or": [self.left.as_structure(), self.right.as_structure()]}

    @classmethod
    def from_structure(cls, structure: JsonStructure) -> "OrPredicate":
        return cls(
            BasePredicate.from_structure(structure["or"][0]),
            BasePredicate.from_structure(structure["or"][1]),
        )


class NotPredicate(LogicallyCombinablePredicate):
    def __init__(self, inverted: BasePredicate) -> None:
        self.inverted = inverted

    def as_structure(self) -> JsonStructure:
        return {"not": self.inverted.as_structure()}

    @classmethod
    def from_structure(cls, structure: JsonStructure) -> "NotPredicate":
        return cls(BasePredicate.from_structure(structure["not"]))


class TcpPredicate(LogicallyCombinablePredicate):
    """Represents a `Mountebank TCP predicate <http://www.mbtest.org/docs/protocols/tcp>`_.
    A predicate can be thought of as a trigger, which may or may not match a request.

    :param data: Data to match the request.
    """

    def __init__(self, data: str) -> None:
        self.data = data

    def as_structure(self) -> JsonStructure:
        return {"contains": {"data": self.data}}

    @classmethod
    def from_structure(cls, structure: JsonStructure) -> "TcpPredicate":
        return cls(structure["contains"]["data"])


class InjectionPredicate(BasePredicate, Injecting):
    """Represents a `Mountebank injection predicate <http://www.mbtest.org/docs/api/injection>`_.
    A predicate can be thought of as a trigger, which may or may not match a request.

    Injection requires Mountebank version 2.0 or higher.

    :param inject: JavaScript function to inject.
    """

    @classmethod
    def from_structure(cls, structure: JsonStructure) -> "InjectionPredicate":
        return cls(inject=structure["inject"])
