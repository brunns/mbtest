# encoding=utf-8
from __future__ import unicode_literals, absolute_import, division, print_function
from abc import ABCMeta, abstractmethod
from six import add_metaclass


@add_metaclass(ABCMeta)
class JsonSerializable(object):
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

    def _set_if_in_dict(self, dictionary, key, name):
        if key in dictionary:
            setattr(self, name, dictionary[key])
