# encoding=utf-8
from abc import ABCMeta, abstractmethod
from typing import Any, Mapping, MutableMapping

# JsonStructure = Union[MutableMapping[str, "Structure"], Iterable["Structure"], str, int, bool]
JsonStructure = Any  # Pending a better solution to https://github.com/python/typing/issues/182


class JsonSerializable(metaclass=ABCMeta):
    @abstractmethod
    def as_structure(self) -> JsonStructure:  # pragma: no cover
        """
        :returns Structure suitable for JSON serialisation.
        :rtype: dict
        """
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def from_structure(structure: JsonStructure) -> "JsonSerializable":  # pragma: no cover
        raise NotImplementedError()

    @staticmethod
    def _add_if_true(dictionary: MutableMapping[str, Any], key: str, value: Any) -> None:
        if value:
            dictionary[key] = value

    def _set_if_in_dict(self, dictionary: Mapping[str, Any], key: str, name: str) -> None:
        if key in dictionary:
            setattr(self, name, dictionary[key])

    def __repr__(self) -> str:  # pragma: no cover
        state = ("{0:s}={1!r:s}".format(attr, value) for (attr, value) in vars(self).items())
        return "{0:s}.{1:s}({2:s})".format(
            self.__class__.__module__, self.__class__.__name__, ", ".join(state)
        )
