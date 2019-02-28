# encoding=utf-8
from mbtest.imposters.base import JsonSerializable
from mbtest.imposters.behaviors.using import Using


class Lookup(JsonSerializable):
    def __init__(self, key, datasource_path, datasource_key_column, into):
        self.key = key
        self.datasource_path = datasource_path
        self.datasource_key_column = datasource_key_column
        self.into = into

    def as_structure(self):
        return {
            "key": self.key.as_structure(),
            "fromDataSource": {
                "csv": {"path": self.datasource_path, "keyColumn": self.datasource_key_column}
            },
            "into": self.into,
        }

    @staticmethod
    def from_structure(structure):
        return Lookup(
            Key.from_structure(structure["key"]),
            structure["fromDataSource"]["csv"]["path"],
            structure["fromDataSource"]["csv"]["keyColumn"],
            structure["into"],
        )


class Key(JsonSerializable):
    def __init__(self, from_, using, index=0):
        self.from_ = from_
        self.using = using
        self.index = index

    def as_structure(self):
        return {"from": self.from_, "using": self.using.as_structure(), "index": self.index}

    @staticmethod
    def from_structure(structure):
        return Key(structure["from"], Using.from_structure(structure["using"]), structure["index"])
