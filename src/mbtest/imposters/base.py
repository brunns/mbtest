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
    def _add_if_true(dictionary, key, value):
        if value:
            dictionary[key] = value
