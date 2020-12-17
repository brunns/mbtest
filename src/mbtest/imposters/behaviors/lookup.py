# encoding=utf-8
from pathlib import Path
from typing import Union

from mbtest.imposters.base import JsonSerializable, JsonStructure
from mbtest.imposters.behaviors.using import Using


class Lookup(JsonSerializable):
    """Represents a `lookup behavior <http://www.mbtest.org/docs/api/behaviors#behavior-lookup>`_.

    :param key: How to select the key from the request.
    :param datasource_path: The path to the data source.
    :param datasource_key_column: The header of the column to match against the key.
    :param into: The token to replace in the response with the selected request value.
    """

    def __init__(
        self, key: "Key", datasource_path: Union[str, Path], datasource_key_column: str, into: str
    ):
        self.key = key
        self.datasource_path = datasource_path
        self.datasource_key_column = datasource_key_column
        self.into = into

    def as_structure(self) -> JsonStructure:
        return {
            "key": self.key.as_structure(),
            "fromDataSource": {
                "csv": {"path": str(self.datasource_path), "keyColumn": self.datasource_key_column}
            },
            "into": self.into,
        }

    @classmethod
    def from_structure(cls, structure: JsonStructure) -> "Lookup":
        return cls(
            Key.from_structure(structure["key"]),
            structure["fromDataSource"]["csv"]["path"],
            structure["fromDataSource"]["csv"]["keyColumn"],
            structure["into"],
        )


class Key(JsonSerializable):
    """The information on how to select the key from the request.

    :param from_: The name of the request field to copy from, or, if the request field is an object, then an object
        specifying the path to the request field.
    :param using: The configuration needed to select values from the response
    :param index: Index of the iten from the result array to be selected.
    """

    def __init__(self, from_: str, using: Using, index: int = 0) -> None:
        self.from_ = from_
        self.using = using
        self.index = index

    def as_structure(self) -> JsonStructure:
        return {"from": self.from_, "using": self.using.as_structure(), "index": self.index}

    @classmethod
    def from_structure(cls, structure: JsonStructure) -> "Key":
        return cls(structure["from"], Using.from_structure(structure["using"]), structure["index"])
