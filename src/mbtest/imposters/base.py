# encoding=utf-8
from abc import ABCMeta, abstractmethod


class JsonSerializable(metaclass=ABCMeta):
    @abstractmethod
    def as_structure(self):  # pragma: no cover
        """
        :returns Structure suitable for JSON serialisation.
        :rtype: dict
        """
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def from_structure(structure):  # pragma: no cover
        raise NotImplementedError()

    @staticmethod
    def _add_if_true(dictionary, key, value):
        if value:
            dictionary[key] = value

    def _set_if_in_dict(self, dictionary, key, name):
        if key in dictionary:
            setattr(self, name, dictionary[key])

    def __repr__(self):  # pragma: no cover
        state = (
            "{0:s}={1!r:s}".format(attribute, value) for (attribute, value) in self.__dict__.items()
        )
        return "{0:s}.{1:s}({2:s})".format(
            self.__class__.__module__, self.__class__.__name__, ", ".join(state)
        )
