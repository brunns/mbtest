from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable, MutableMapping, Sequence
from dataclasses import dataclass
from typing import Any, TypeAlias, TypeVar, cast

_T = TypeVar("_T")

# JsonStructure: TypeAlias = str | int | float | bool | None | list[JsonStructure] | dict[str, JsonStructure]
JsonStructure: TypeAlias = Any  # TODO Pending a better solution to https://github.com/python/typing/issues/182


@dataclass
class JsonSerializable(ABC):
    """Object capable of being converted to a JSON serializable structure (using :py:meth:`as_structure`)
    or from such a structure ((using :py:meth:`from_structure`).
    """

    @abstractmethod
    def as_structure(self) -> JsonStructure:  # pragma: no cover
        """Converted to a JSON serializable structure.

        :returns: Structure suitable for JSON serialisation.
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def from_structure(cls, structure: JsonStructure) -> JsonSerializable:  # pragma: no cover
        """Converted from a JSON serializable structure.

        :param structure: JSON structure to be converted.

        :returns: Converted object.
        """
        raise NotImplementedError

    @staticmethod
    def add_if_true(dictionary: MutableMapping[str, Any], key: str, value: Any) -> None:
        """Add key/value to dictionary only if value is truthy."""
        if value:
            dictionary[key] = value

    @staticmethod
    def one_or_many(value: _T | Iterable[_T] | None) -> list[_T] | None:
        """Normalise None / a single item / an iterable to a list, or None."""
        if value is None:
            return None
        if isinstance(value, Sequence):
            return list(cast("Iterable[_T]", value))
        return cast("list[_T]", [value])


@dataclass
class Injecting(JsonSerializable, ABC):
    inject: str

    def as_structure(self) -> JsonStructure:
        return {"inject": self.inject}
