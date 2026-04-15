from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from mbtest.imposters.base import JsonSerializable, JsonStructure
from mbtest.imposters.behaviors.using import Using


@dataclass
class Lookup(JsonSerializable):
    """Represents a `lookup behavior <http://localhost:2525/docs/api/behaviors#behavior-lookup>`_.

    :param key: How to select the key from the request.
    :param datasource_path: The path to the data source.
    :param datasource_key_column: The header of the column to match against the key.
    :param into: The token to replace in the response with the selected request value.
    """

    key: Key
    datasource_path: str | Path
    datasource_key_column: str
    into: str

    def as_structure(self) -> JsonStructure:
        return {
            "key": self.key.as_structure(),
            "fromDataSource": {"csv": {"path": str(self.datasource_path), "keyColumn": self.datasource_key_column}},
            "into": self.into,
        }

    @classmethod
    def from_structure(cls, structure: JsonStructure) -> Lookup:
        return cls(
            Key.from_structure(structure["key"]),
            structure["fromDataSource"]["csv"]["path"],
            structure["fromDataSource"]["csv"]["keyColumn"],
            structure["into"],
        )


@dataclass
class Key(JsonSerializable):
    """The information on how to select the key from the request.

    :param from_: The name of the request field to copy from, or, if the request field is an object, then an object
        specifying the path to the request field.
    :param using: The configuration needed to select values from the response
    :param index: Index of the iten from the result array to be selected.
    """

    from_: str
    using: Using
    index: int = 0

    def as_structure(self) -> JsonStructure:
        return {"from": self.from_, "using": self.using.as_structure(), "index": self.index}

    @classmethod
    def from_structure(cls, structure: JsonStructure) -> Key:
        return cls(structure["from"], Using.from_structure(structure["using"]), structure["index"])
