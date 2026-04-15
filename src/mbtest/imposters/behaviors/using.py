from __future__ import annotations

import abc
from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from typing import cast

from mbtest.imposters.base import JsonSerializable, JsonStructure


@dataclass
class Using(JsonSerializable, abc.ABC):
    """
    How to select values from the response.

    :param selector: The selector used to select the value(s) from the request.
    """

    class Method(Enum):
        REGEX = "regex"
        XPATH = "xpath"
        JSONPATH = "jsonpath"

    selector: str

    @property
    @abc.abstractmethod
    def method(self) -> Using.Method:  # pragma: no cover
        raise NotImplementedError

    def as_structure(self) -> JsonStructure:
        return {"method": self.method.value, "selector": self.selector}

    @classmethod
    def from_structure(cls, structure: JsonStructure) -> Using:
        method = cls.Method(structure["method"])
        return cast(
            "type[Using]",
            {
                cls.Method.REGEX: UsingRegex,
                cls.Method.XPATH: UsingXpath,
                cls.Method.JSONPATH: UsingJsonpath,
            }[method],
        ).from_structure(structure)


@dataclass
class UsingRegex(Using):
    """
    `Select values from the response using a regular expression. <http://localhost:2525/docs/api/behaviors#copy-regex-replacement>`_

    :param selector: The selector used to select the value(s) from the request.
    :param ignore_case: Uses a case-insensitive regular expression
    :param multiline: Uses a multiline regular expression
    """

    ignore_case: bool = False
    multiline: bool = False

    @property
    def method(self) -> Using.Method:
        return Using.Method.REGEX

    def as_structure(self) -> JsonStructure:
        structure = super().as_structure()
        structure["options"] = {
            "ignoreCase": self.ignore_case,
            "multiline": self.multiline,
        }
        return structure

    @classmethod
    def from_structure(cls, structure: JsonStructure) -> UsingRegex:
        return cls(
            selector=structure["selector"],
            ignore_case=structure["options"]["ignoreCase"],
            multiline=structure["options"]["multiline"],
        )


@dataclass
class UsingXpath(Using):
    """
    `Select values from the response using an xpath expression. <http://localhost:2525/docs/api/behaviors#copy-xpath-replacement>`_

    :param selector: The selector used to select the value(s) from the request.
    :param ns: The ns object maps namespace aliases to URLs
    """

    ns: Mapping[str, str] | None = None

    @property
    def method(self) -> Using.Method:
        return Using.Method.XPATH

    def as_structure(self) -> JsonStructure:
        structure = super().as_structure()
        if self.ns:
            structure["ns"] = self.ns
        return structure

    @classmethod
    def from_structure(cls, structure: JsonStructure) -> UsingXpath:
        return cls(
            selector=structure["selector"],
            ns=structure.get("ns"),
        )


@dataclass
class UsingJsonpath(Using):
    """
    `Select values from the response using a jsonpath expression. <http://localhost:2525/docs/api/behaviors#copy-jsonpath-replacement>`_

    :param selector: The selector used to select the value(s) from the request.
    """

    @property
    def method(self) -> Using.Method:
        return Using.Method.JSONPATH

    @classmethod
    def from_structure(cls, structure: JsonStructure) -> UsingJsonpath:
        return cls(selector=structure["selector"])
