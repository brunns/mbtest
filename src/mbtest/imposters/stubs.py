from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Iterable

from mbtest.imposters.base import JsonSerializable, JsonStructure
from mbtest.imposters.predicates import BasePredicate, Predicate
from mbtest.imposters.responses import BaseResponse, Response


class Stub(JsonSerializable):
    """Represents a `Mountebank stub <http://localhost:2525/docs/api/stubs>`_.
    Think of a stub as a behavior, triggered by a matching predicate.

    :param predicates: Trigger this stub if one of these predicates matches the request
    :param responses: Use these response behaviors (in order)
    """

    def __init__(
        self,
        predicates: BasePredicate | Iterable[BasePredicate] | None = None,
        responses: BaseResponse | Iterable[BaseResponse] | None = None,
    ) -> None:
        self.predicates = self.one_or_many(predicates) or [Predicate()]
        self.responses = self.one_or_many(responses) or [Response()]

    def as_structure(self) -> JsonStructure:
        return {
            "predicates": [predicate.as_structure() for predicate in self.predicates],
            "responses": [response.as_structure() for response in self.responses],
        }

    @classmethod
    def from_structure(cls, structure: JsonStructure) -> Stub:
        return cls(
            [BasePredicate.from_structure(p) for p in structure.get("predicates", ())],
            [BaseResponse.from_structure(r) for r in structure.get("responses", ())],
        )


class AddStub(JsonSerializable):
    """Represents a `Mountebank add stub request <http://localhost:2525/docs/api/overview#add-stub>`.
    To add new stab to an existing imposter.

    :param index: The index in imposter stubs array.
     If you leave off the index field, the stub will be added to the end of the existing stubs array.
    :param stub: The stub that will be added to the existing stubs array
    """

    def __init__(
        self,
        stub: Stub | None = None,
        index: int | None = None,
    ) -> None:
        self.index = index
        if stub:
            self.stub = stub
        else:
            self.stub = Stub()

    def as_structure(self) -> JsonStructure:
        structure = {
            "stub": self.stub.as_structure(),
        }
        if self.index is not None:
            structure["index"] = self.index
        return structure

    @classmethod
    def from_structure(cls, structure: JsonStructure) -> AddStub:
        return AddStub(
            index=structure.get("index"),
            stub=Stub.from_structure(structure.get("stub")),
        )
