# encoding=utf-8
from mbtest.imposters.base import JsonSerializable, JsonStructure
from mbtest.imposters.behaviors.using import Using


class Lookup(JsonSerializable):
    """Represents a `lookup behavior <http://www.mbtest.org/docs/api/behaviors#behavior-lookup>`_.

    :param key: TODO
    :param datasource_path: TODO
    :param datasource_key_column: TODO
    :param into: The token to replace in the response with the selected request value.

    """

    def __init__(self, key: "Key", datasource_path: str, datasource_key_column: str, into: str):
        self.key = key
        self.datasource_path = datasource_path
        self.datasource_key_column = datasource_key_column
        self.into = into

    def as_structure(self) -> JsonStructure:
        return {
            "key": self.key.as_structure(),
            "fromDataSource": {
                "csv": {"path": self.datasource_path, "keyColumn": self.datasource_key_column}
            },
            "into": self.into,
        }

    @staticmethod
    def from_structure(structure: JsonStructure) -> "Lookup":
        return Lookup(
            Key.from_structure(structure["key"]),
            structure["fromDataSource"]["csv"]["path"],
            structure["fromDataSource"]["csv"]["keyColumn"],
            structure["into"],
        )


class Key(JsonSerializable):
    """TODO

    :param from_: The name of the request field to copy from, or, if the request field is an object, then an object
        specifying the path to the request field.
    :param using: The configuration needed to select values from the response
    :param index: TODO

    """

    def __init__(self, from_: str, using: Using, index: int = 0) -> None:
        self.from_ = from_
        self.using = using
        self.index = index

    def as_structure(self) -> JsonStructure:
        return {"from": self.from_, "using": self.using.as_structure(), "index": self.index}

    @staticmethod
    def from_structure(structure: JsonStructure) -> "Key":
        return Key(structure["from"], Using.from_structure(structure["using"]), structure["index"])
