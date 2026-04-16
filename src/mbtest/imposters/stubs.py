from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import cast

from mbtest.imposters.base import JsonObject, JsonSerializable
from mbtest.imposters.predicates import BasePredicate, Predicate
from mbtest.imposters.responses import BaseResponse, Response


@dataclass(init=False)
class Stub(JsonSerializable):
    """Represents a `Mountebank stub <http://localhost:2525/docs/api/stubs>`_.
    Think of a stub as a behavior, triggered by a matching predicate.

    :param predicates: Trigger this stub if one of these predicates matches the request
    :param responses: Use these response behaviors (in order)
    """

    predicates: list[BasePredicate]
    responses: list[BaseResponse]

    def __init__(
        self,
        predicates: BasePredicate | Iterable[BasePredicate] | None = None,
        responses: BaseResponse | Iterable[BaseResponse] | None = None,
    ) -> None:
        self.predicates = self.one_or_many(predicates) or [Predicate()]
        self.responses = self.one_or_many(responses) or [Response()]

    def as_structure(self) -> JsonObject:
        return {
            "predicates": [predicate.as_structure() for predicate in self.predicates],
            "responses": [response.as_structure() for response in self.responses],
        }

    @classmethod
    def from_structure(cls, structure: JsonObject) -> Stub:
        return cls(
            [
                BasePredicate.from_structure(cls.as_json_object(p))
                for p in cast("list[JsonObject]", structure.get("predicates", ()))
            ],
            [
                BaseResponse.from_structure(cls.as_json_object(r))
                for r in cast("list[JsonObject]", structure.get("responses", ()))
            ],
        )


@dataclass
class AddStub(JsonSerializable):
    """Represents a `Mountebank add stub request <http://localhost:2525/docs/api/overview#add-stub>`.
    To add new stab to an existing imposter.

    :param index: The index in imposter stubs array.
     If you leave off the index field, the stub will be added to the end of the existing stubs array.
    :param stub: The stub that will be added to the existing stubs array
    """

    stub: Stub = field(default_factory=Stub)
    index: int | None = None

    def as_structure(self) -> JsonObject:
        structure: JsonObject = {"stub": self.stub.as_structure()}
        if self.index is not None:
            structure["index"] = self.index
        return structure

    @classmethod
    def from_structure(cls, structure: JsonObject) -> AddStub:
        return cls(
            stub=Stub.from_structure(cls.as_json_object(structure.get("stub", {}))),
            index=cast("int | None", structure.get("index")),
        )
