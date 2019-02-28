# encoding=utf-8
from mbtest.imposters.base import JsonSerializable
from mbtest.imposters.behaviors.using import Using


class Copy(JsonSerializable):
    """Represents a copy behavior - see http://www.mbtest.org/docs/api/behaviors#behavior-copy"""

    def __init__(self, from_, into, using):
        """
        :param from_: The name of the request field to copy from, or, if the request field is an object, then an object
        specifying the path to the request field.
        :type from_: str or dict(str, str)
        :param into: The token to replace in the response with the selected request value.
        :type into: str
        :param using: The configuration needed to select values from the response
        :type using: mbtest.imposters.behaviors.using.Using
        """
        self.from_ = from_
        self.into = into
        self.using = using

    def as_structure(self):
        return {"from": self.from_, "into": self.into, "using": self.using.as_structure()}

    @staticmethod
    def from_structure(structure):
        return Copy(structure["from"], structure["into"], Using.from_structure(structure["using"]))
