# encoding=utf-8
from mbtest.imposters.base import JsonSerializable


class Lookup(JsonSerializable):
    def __init__(self, key, datasource_path, datasource_row, into):
        self.key = key
        self.datasource_path = datasource_path
        self.datasource_key_column = datasource_row
        self.into = into

    def as_structure(self):
        return {
            "key": self.key.as_structure(),
            "fromDataSource": {"csv": {"path": self.datasource_path, "keyColumn": self.datasource_key_column}},
            "into": self.into,
        }


class Key(JsonSerializable):
    def __init__(self, from_, using, index=0):
        self.from_ = from_
        self.using = using
        self.index = index

    def as_structure(self):
        return {"from": self.from_, "using": self.using.as_structure(), "index": self.index}
