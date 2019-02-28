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
