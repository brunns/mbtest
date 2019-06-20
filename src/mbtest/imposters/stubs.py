# encoding=utf-8
from collections.abc import Sequence
from enum import Enum
from typing import Iterable, Mapping, Optional, Union

from furl import furl
from mbtest.imposters.base import JsonSerializable, JsonStructure
from mbtest.imposters.predicates import Predicate
from mbtest.imposters.responses import Response


class Stub(JsonSerializable):
    """Represents a Mountebank stub - see http://www.mbtest.org/docs/api/stubs.
    Think of a stub as a behavior, triggered by a matching predicate.
    """

    def __init__(
        self,
        predicates: Optional[Union[Predicate, Iterable[Predicate]]] = None,
        responses: Optional[Union[Response, Iterable[Response], "Proxy", Iterable["Proxy"]]] = None,
    ) -> None:
        """
        :param predicates: Trigger this stub if one of these predicates matches the request
        :type predicates: Predicate or list(Predicate)
        :param responses: Use these response behaviors (in order)
        :type responses: Response or list(Response)
        """
        if predicates:
            self.predicates = predicates if isinstance(predicates, Sequence) else [predicates]
        else:
            self.predicates = [Predicate()]
        if responses:
            self.responses = responses if isinstance(responses, Sequence) else [responses]
        else:
            self.responses = [Response()]

    def as_structure(self) -> JsonStructure:
        return {
            "predicates": [predicate.as_structure() for predicate in self.predicates],
            "responses": [response.as_structure() for response in self.responses],
        }

    @staticmethod
    def from_structure(structure: JsonStructure) -> "Stub":
        responses = []
        for response in structure.get("responses", ()):
            if "proxy" in response:
                responses.append(Proxy.from_structure(response))
            else:
                responses.append(Response.from_structure(response))
        return Stub(
            [Predicate.from_structure(predicate) for predicate in structure.get("predicates", ())],
            responses,
        )


class Proxy(JsonSerializable):
    class Mode(Enum):
        ONCE = "proxyOnce"
        ALWAYS = "proxyAlways"
        TRANSPARENT = "proxyTransparent"

    def __init__(
        self,
        to: Union[furl, str],
        wait: Optional[int] = None,
        inject_headers: Optional[Mapping[str, str]] = None,
        mode: "Proxy.Mode" = Mode.ALWAYS,
    ) -> None:
        self.to = to
        self.wait = wait
        self.inject_headers = inject_headers
        self.mode = mode

    def as_structure(self) -> JsonStructure:
        proxy = {
            "to": self.to.url if isinstance(self.to, furl) else self.to,
            "mode": self.mode.value,
        }
        self._add_if_true(proxy, "injectHeaders", self.inject_headers)
        response = {"proxy": proxy}
        if self.wait:
            response["_behaviors"] = {"wait": self.wait}
        return response

    @staticmethod
    def from_structure(structure: JsonStructure) -> "Proxy":
        proxy_structure = structure["proxy"]
        proxy = Proxy(
            to=furl(proxy_structure["to"]),
            inject_headers=proxy_structure["injectHeaders"]
            if "injectHeaders" in proxy_structure
            else None,
            mode=Proxy.Mode(proxy_structure["mode"]),
        )
        wait = structure.get("_behaviors", {}).get("wait")
        if wait:
            proxy.wait = wait
        return proxy
