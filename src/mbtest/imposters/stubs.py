# encoding=utf-8
from __future__ import unicode_literals, absolute_import, division, print_function
from six import PY3
from mbtest.imposters.base import JsonSerializable
from mbtest.imposters.predicates import Predicate
from mbtest.imposters.responses import Response

if PY3:
    from collections.abc import Sequence
else:  # pragma: no cover
    from collections import Sequence


class Stub(JsonSerializable):
    """Represents a Mountebank stub - see http://www.mbtest.org/docs/api/stubs.
    Think of a stub as a behavior, triggered by a matching predicate.
    """

    def __init__(self, predicates=None, responses=None):
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

    def as_structure(self):
        return {
            "predicates": [predicate.as_structure() for predicate in self.predicates],
            "responses": [response.as_structure() for response in self.responses],
        }

    @staticmethod
    def from_structure(structure):
        responses = []
        for response in structure.get("responses", ()):
            if "proxy" in response:
                responses.append(Proxy.from_structure(response))
            else:
                responses.append(Response.from_structure(response))
        return Stub([Predicate.from_structure(predicate) for predicate in structure.get("predicates", ())], responses)


class Proxy(JsonSerializable):
    def __init__(self, to, wait=None):
        self.to = to
        self.wait = wait

    def as_structure(self):
        response = {"proxy": {"to": self.to}}
        if self.wait:
            response["_behaviors"] = {"wait": self.wait}
        return response

    @staticmethod
    def from_structure(structure):
        proxy_structure = structure["proxy"]
        proxy = Proxy(proxy_structure["to"])
        wait = structure.get("_behaviors", {}).get("wait")
        if wait:
            proxy.wait = wait
        return proxy
