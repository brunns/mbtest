# encoding=utf-8
from abc import ABC, abstractmethod
from typing import Any, Mapping, MutableMapping

# JsonStructure = Union[MutableMapping[str, "JsonStructure"], Iterable["JsonStructure"], str, int, bool, None]
JsonStructure = Any  # TODO Pending a better solution to https://github.com/python/typing/issues/182


class JsonSerializable(ABC):
    """Object capable of being converted to a JSON serializable structure (using :py:meth:`as_structure`)
    or from such a structure ((using :py:meth:`from_structure`).
    """

    @abstractmethod
    def as_structure(self) -> JsonStructure:  # pragma: no cover
        """Converted to a JSON serializable structure.

        :returns: Structure suitable for JSON serialisation.
        """
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def from_structure(cls, structure: JsonStructure) -> "JsonSerializable":  # pragma: no cover
        """Converted from a JSON serializable structure.

        :param structure: JSON structure to be converted.

        :returns: Converted object.
        """
        raise NotImplementedError()

    @staticmethod
    def add_if_true(dictionary: MutableMapping[str, Any], key: str, value: Any) -> None:
        if value:
            dictionary[key] = value

    def set_if_in_dict(self, dictionary: Mapping[str, Any], key: str, name: str) -> None:
        if key in dictionary:
            setattr(self, name, dictionary[key])

    def __repr__(self) -> str:  # pragma: no cover
        state = (f"{attr:s}={value!r:s}" for (attr, value) in vars(self).items())
        return f"{self.__class__.__module__:s}.{self.__class__.__name__:s}({', '.join(state):s})"


class Injecting(JsonSerializable, ABC):
    def __init__(self, inject: str) -> None:
        self.inject = inject

    def as_structure(self) -> JsonStructure:
        return {"inject": self.inject}
