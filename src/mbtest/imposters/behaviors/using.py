# encoding=utf-8
import abc
from enum import Enum

from six import add_metaclass

from mbtest.imposters.base import JsonSerializable


@add_metaclass(abc.ABCMeta)
class Using(JsonSerializable):
    class Method(Enum):
        REGEX = "regex"
        XPATH = "xpath"
        JSONPATH = "jsonpath"

    def __init__(self, method, selector):
        """
        :param method: The method used to select the value(s) from the request.
        :type method: Using.Method
        :param selector: The selector used to select the value(s) from the request.
        :type selector: str
        """
        self.method = method
        self.selector = selector

    def as_structure(self):
        return {"method": self.method.value, "selector": self.selector}


class UsingRegex(Using):
    def __init__(self, selector, ignore_case=False):
        """
        :param selector: The selector used to select the value(s) from the request.
        :type selector: str
        :param ignore_case: Uses a case-insensitive regular expression (For REGEX method)
        :type ignore_case: bool
        """
        super(UsingRegex, self).__init__(Using.Method.REGEX, selector)
        self.ignore_case = ignore_case

    def as_structure(self):
        structure = super(UsingRegex, self).as_structure()
        structure["options"] = {"ignoreCase": self.ignore_case}
        return structure


class UsingXpath(Using):
    def __init__(self, selector, ns=None):
        """
        :param selector: The selector used to select the value(s) from the request.
        :type selector: str
        :param ns: The ns object maps namespace aliases to URLs
        :type ns: dict(str, str)
        """
        super(UsingXpath, self).__init__(Using.Method.XPATH, selector)
        self.ns = ns

    def as_structure(self):
        structure = super(UsingXpath, self).as_structure()
        if self.ns:
            structure["ns"] = self.ns
        return structure


class UsingJsonpath(Using):
    def __init__(self, selector):
        """
        :param selector: The selector used to select the value(s) from the request.
        :type selector: str
        """
        super(UsingJsonpath, self).__init__(Using.Method.JSONPATH, selector)
