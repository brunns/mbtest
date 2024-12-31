from collections.abc import Mapping, Sequence
from functools import singledispatch
from xml.etree import ElementTree as ET


def data2xml(data, default_namespace=None) -> ET.Element:
    """Convert data structure to XML
    :param data: data to convert to XML
    :param default_namespace: Namespace
    :returns: Element
    """
    root, body = data.popitem()
    root = ET.Element(root)
    if default_namespace:
        root.set(f"xmlns:{default_namespace[0]}", default_namespace[1])
    return buildxml(body, root)


def et2string(element: ET.Element) -> str:
    return ET.tostring(element, encoding="unicode")


@singledispatch
def buildxml(data, root) -> ET.Element:
    root.text = str(data)
    return root


@buildxml.register(Mapping)
def buildxml_mapping(data, root) -> ET.Element:
    for key, value in data.items():
        s = ET.SubElement(root, key)
        buildxml(value, s)
    return root


@buildxml.register(Sequence)
def buildxml_sequence(data: Sequence, root: ET.Element) -> ET.Element:
    for value in data:
        buildxml(value, root)
    return root


@buildxml.register(str)
def buildxml_basestring(data: str, root) -> ET.Element:
    root.text = data
    return root
