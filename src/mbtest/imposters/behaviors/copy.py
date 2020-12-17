# encoding=utf-8
from typing import Mapping, Union

from mbtest.imposters.base import JsonSerializable, JsonStructure
from mbtest.imposters.behaviors.using import Using


class Copy(JsonSerializable):
    """Represents a `copy behavior <http://www.mbtest.org/docs/api/behaviors#behavior-copy>`_.

    :param from_: The name of the request field to copy from, or, if the request field is an object, then an object
        specifying the path to the request field.
    :param into: The token to replace in the response with the selected request value.
    :param using: The configuration needed to select values from the response.
    """

    def __init__(self, from_: Union[str, Mapping[str, str]], into: str, using: Using) -> None:
        self.from_ = from_
        self.into = into
        self.using = using

    def as_structure(self) -> JsonStructure:
        return {"from": self.from_, "into": self.into, "using": self.using.as_structure()}

    @classmethod
    def from_structure(cls, structure: JsonStructure) -> "Copy":
        return cls(structure["from"], structure["into"], Using.from_structure(structure["using"]))
