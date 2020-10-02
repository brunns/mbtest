# encoding=utf-8
from collections.abc import Mapping, Sequence
from functools import singledispatch
from xml.etree import ElementTree as et


def data2xml(data, default_namespace=None) -> et.Element:
    """ Convert data structure to XML
    :param data: data to convert to XML
    :param default_namespace: Namespace
    :returns: Element
    """
    root, body = data.popitem()
    root = et.Element(root)
    if default_namespace:
        root.set(f"xmlns:{default_namespace[0]}", default_namespace[1])
    return buildxml(body, root)


def et2string(element):
    return et.tostring(element, encoding="unicode")


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


@buildxml.register(str)
def buildxml_basestring(data, root):
    root.text = data
    return root
