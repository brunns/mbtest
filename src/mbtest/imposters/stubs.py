from collections.abc import Iterable, Sequence
from typing import Optional, Union, cast

from mbtest.imposters.base import JsonSerializable, JsonStructure
from mbtest.imposters.predicates import BasePredicate, Predicate
from mbtest.imposters.responses import BaseResponse, InjectionResponse, Proxy, Response


class Stub(JsonSerializable):
    """Represents a `Mountebank stub <http://www.mbtest.org/docs/api/stubs>`_.
    Think of a stub as a behavior, triggered by a matching predicate.

    :param predicates: Trigger this stub if one of these predicates matches the request
    :param responses: Use these response behaviors (in order)
    """

    def __init__(
        self,
        predicates: Optional[Union[BasePredicate, Iterable[BasePredicate]]] = None,
        responses: Optional[Union[BaseResponse, Iterable[BaseResponse]]] = None,
    ) -> None:
        if predicates:
            self.predicates = cast(
                Iterable[BasePredicate],
                predicates if isinstance(predicates, Sequence) else [predicates],
            )
        else:
            self.predicates = [Predicate()]
        if responses:
            self.responses = cast(
                Iterable[BaseResponse],
                responses if isinstance(responses, Sequence) else [responses],
            )
        else:
            self.responses = [Response()]

    def as_structure(self) -> JsonStructure:
        return {
            "predicates": [predicate.as_structure() for predicate in self.predicates],
            "responses": [response.as_structure() for response in self.responses],
        }

    @classmethod
    def from_structure(cls, structure: JsonStructure) -> "Stub":
        responses: list[Union[InjectionResponse, Proxy, Response]] = []
        for response in structure.get("responses", ()):
            if "proxy" in response:
                responses.append(Proxy.from_structure(response))
            elif "inject" in response:
                responses.append(InjectionResponse.from_structure(response))
            else:
                responses.append(Response.from_structure(response))
        return cls(
            [BasePredicate.from_structure(predicate) for predicate in structure.get("predicates", ())],
            responses,
        )


class AddStub(JsonSerializable):
    """Represents a `Mountebank add stub request <http://www.mbtest.org/docs/api/overview#add-stub>`.
    To add new stab to an existing imposter.

    :param index: The index in imposter stubs array.
     If you leave off the index field, the stub will be added to the end of the existing stubs array.
    :param stub: The stub that will be added to the existing stubs array
    """

    def __init__(
        self,
        stub: Optional[Stub] = None,
        index: Optional[int] = None,
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
    def from_structure(cls, structure: JsonStructure) -> "AddStub":
        return AddStub(
            index=structure.get("index"),
            stub=Stub.from_structure(structure.get("stub")),
        )
