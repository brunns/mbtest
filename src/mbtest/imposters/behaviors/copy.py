from __future__ import annotations

from dataclasses import dataclass
from typing import cast

from mbtest.imposters.base import JsonObject, JsonSerializable, JsonValue  # noqa: F401
from mbtest.imposters.behaviors.using import Using


@dataclass
class Copy(JsonSerializable):
    """Represents a `copy behavior <http://localhost:2525/docs/api/behaviors#behavior-copy>`_.

    :param from_: The name of the request field to copy from, or, if the request field is an object, then an object
        specifying the path to the request field.
    :param into: The token to replace in the response with the selected request value.
    :param using: The configuration needed to select values from the response.
    """

    from_: str | JsonObject
    into: str
    using: Using

    def as_structure(self) -> JsonObject:
        return {"from": self.from_, "into": self.into, "using": self.using.as_structure()}

    @classmethod
    def from_structure(cls, structure: JsonObject) -> Copy:
        from_raw = cast("str | JsonObject", structure["from"])
        return cls(
            from_raw, cast("str", structure["into"]), Using.from_structure(cls.as_json_object(structure["using"]))
        )
