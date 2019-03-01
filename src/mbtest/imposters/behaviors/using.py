# encoding=utf-8
import abc
from enum import Enum

from mbtest.imposters.base import JsonSerializable


class Using(JsonSerializable, metaclass=abc.ABCMeta):
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

    @staticmethod
    def from_structure(structure):
        method = Using.Method(structure["method"])
        cls = {
            Using.Method.REGEX: UsingRegex,
            Using.Method.XPATH: UsingXpath,
            Using.Method.JSONPATH: UsingJsonpath,
        }[method]
        return cls.from_structure(structure)


class UsingRegex(Using):
    def __init__(self, selector, ignore_case=False, multiline=False):
        """
        :param selector: The selector used to select the value(s) from the request.
        :type selector: str
        :param ignore_case: Uses a case-insensitive regular expression
        :type ignore_case: bool
        :param multiline: Uses a multiline regular expression
        :type multiline: bool
        """
        super().__init__(Using.Method.REGEX, selector)
        self.ignore_case = ignore_case
        self.multiline = multiline

    def as_structure(self):
        structure = super().as_structure()
        structure["options"] = {"ignoreCase": self.ignore_case, "multiline": self.multiline}
        return structure

    @staticmethod
    def from_structure(structure):
        return UsingRegex(
            selector=structure["selector"],
            ignore_case=structure["options"]["ignoreCase"],
            multiline=structure["options"]["multiline"],
        )


class UsingXpath(Using):
    def __init__(self, selector, ns=None):
        """
        :param selector: The selector used to select the value(s) from the request.
        :type selector: str
        :param ns: The ns object maps namespace aliases to URLs
        :type ns: dict(str, str)
        """
        super().__init__(Using.Method.XPATH, selector)
        self.ns = ns

    def as_structure(self):
        structure = super().as_structure()
        if self.ns:
            structure["ns"] = self.ns
        return structure

    @staticmethod
    def from_structure(structure):
        using = UsingXpath(selector=structure["selector"])
        using._set_if_in_dict(structure, "ns", "ns")
        return using


class UsingJsonpath(Using):
    def __init__(self, selector):
        """
        :param selector: The selector used to select the value(s) from the request.
        :type selector: str
        """
        super().__init__(Using.Method.JSONPATH, selector)

    @staticmethod
    def from_structure(structure):
        return UsingJsonpath(selector=structure["selector"])
