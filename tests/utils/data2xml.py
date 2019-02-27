# encoding=utf-8
from __future__ import unicode_literals, absolute_import, division, print_function

import xml.etree.ElementTree as et

from six import PY3

if PY3:
    from collections.abc import Mapping
    from collections.abc import Sequence
else:  # pragma: no cover
    from collections import Mapping
    from collections import Sequence
try:
    from functools import singledispatch
except ImportError:
    from singledispatch import singledispatch


def data2xml(data, default_namespace=None):
    """ Convert data structure to XML
    :param data: data to convert to XML
    :type data: dict
    :param default_namespace: Namespace
    :type default_namespace: tuple(str)
    :rtype: xml.etree.ElementTree.Element
    """
    root, body = data.popitem()
    root = et.Element(root)
    if default_namespace:
        root.set("xmlns:{0}".format(default_namespace[0]), default_namespace[1])
    return buildxml(body, root)


def et2string(element):
    return et.tostring(element, encoding="unicode" if PY3 else "utf-8")


@singledispatch
def buildxml(data, root):
    root.text = str(data)
    return root


@buildxml.register(Mapping)
def buildxml_mapping(data, root):
    for key, value in data.items():
        s = et.SubElement(root, key)
        buildxml(value, s)
    return root


@buildxml.register(Sequence)
def buildxml_sequence(data, root):
    for value in data:
        buildxml(value, root)
        # root.extend(sub)
    return root


try:
    basestring
except NameError:
    basestring = str


@buildxml.register(basestring)
def buildxml_basestring(data, root):
    root.text = data
    return root
