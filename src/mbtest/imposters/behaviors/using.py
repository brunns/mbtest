# encoding=utf-8
import abc
from enum import Enum
from typing import Mapping, Optional, Type, cast

from mbtest.imposters.base import JsonSerializable, JsonStructure


class Using(JsonSerializable, abc.ABC):
    """
    How to select values from the response.

    :param method: The method used to select the value(s) from the request.
    :param selector: The selector used to select the value(s) from the request.
    """

    class Method(Enum):
        REGEX = "regex"
        XPATH = "xpath"
        JSONPATH = "jsonpath"

    def __init__(self, method: Method, selector: str) -> None:
        self.method = method
        self.selector = selector

    def as_structure(self) -> JsonStructure:
        return {"method": self.method.value, "selector": self.selector}

    @classmethod
    def from_structure(cls, structure: JsonStructure) -> "Using":
        method = cls.Method(structure["method"])
        return cast(
            Type["Using"],
            {
                cls.Method.REGEX: UsingRegex,
                cls.Method.XPATH: UsingXpath,
                cls.Method.JSONPATH: UsingJsonpath,
            }[method],
        ).from_structure(structure)


class UsingRegex(Using):
    """
    `Select values from the response using a regular expression. <http://www.mbtest.org/docs/api/behaviors#copy-regex-replacement>`_

    :param selector: The selector used to select the value(s) from the request.
    :param ignore_case: Uses a case-insensitive regular expression
    :param multiline: Uses a multiline regular expression
    """

    def __init__(self, selector: str, ignore_case: bool = False, multiline: bool = False) -> None:
        super().__init__(Using.Method.REGEX, selector)
        self.ignore_case = ignore_case
        self.multiline = multiline

    def as_structure(self) -> JsonStructure:
        structure = super().as_structure()
        structure["options"] = {"ignoreCase": self.ignore_case, "multiline": self.multiline}
        return structure

    @classmethod
    def from_structure(cls, structure: JsonStructure) -> "UsingRegex":
        return cls(
            selector=structure["selector"],
            ignore_case=structure["options"]["ignoreCase"],
            multiline=structure["options"]["multiline"],
        )


class UsingXpath(Using):
    """
    `Select values from the response using an xpath expression. <http://www.mbtest.org/docs/api/behaviors#copy-xpath-replacement>`_

    :param selector: The selector used to select the value(s) from the request.
    :param ns: The ns object maps namespace aliases to URLs
    """

    def __init__(self, selector: str, ns: Optional[Mapping[str, str]] = None) -> None:
        super().__init__(Using.Method.XPATH, selector)
        self.ns = ns

    def as_structure(self) -> JsonStructure:
        structure = super().as_structure()
        if self.ns:
            structure["ns"] = self.ns
        return structure

    @classmethod
    def from_structure(cls, structure: JsonStructure) -> "UsingXpath":
        using = cls(selector=structure["selector"])
        using.set_if_in_dict(structure, "ns", "ns")
        return using


class UsingJsonpath(Using):
    """
    `Select values from the response using a jsonpath expression. <http://www.mbtest.org/docs/api/behaviors#copy-jsonpath-replacement>`_

    :param selector: The selector used to select the value(s) from the request.
    """

    def __init__(self, selector: str) -> None:
        super().__init__(Using.Method.JSONPATH, selector)

    @classmethod
    def from_structure(cls, structure) -> "UsingJsonpath":
        return cls(selector=structure["selector"])
