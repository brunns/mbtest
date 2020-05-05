# encoding=utf-8
from collections.abc import Sequence
from typing import Iterable, List, Optional, Union

from mbtest.imposters.base import JsonSerializable, JsonStructure
from mbtest.imposters.predicates import BasePredicate, Predicate
from mbtest.imposters.responses import BaseResponse, Proxy, Response


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
            self.predicates = predicates if isinstance(predicates, Sequence) else [predicates]
        else:
            self.predicates = [Predicate()]
        if responses:
            self.responses = responses if isinstance(responses, Sequence) else [responses]
        else:
            self.responses = [Response()]

    def as_structure(self) -> JsonStructure:
        return {
            "predicates": [predicate.as_structure() for predicate in self.predicates],
            "responses": [response.as_structure() for response in self.responses],
        }

    @staticmethod
    def from_structure(structure: JsonStructure) -> "Stub":
        responses = []  # type: List[Union[Proxy, Response]]
        for response in structure.get("responses", ()):
            if "proxy" in response:
                responses.append(Proxy.from_structure(response))
            else:
                responses.append(Response.from_structure(response))
        return Stub(
            [Predicate.from_structure(predicate) for predicate in structure.get("predicates", ())],
            responses,
        )
