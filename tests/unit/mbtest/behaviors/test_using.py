# encoding=utf-8
import logging

from mbtest.imposters.behaviors.using import Using
from tests.utils.builders import a_using_regex, a_using_jsonpath, a_using_xpath

logger = logging.getLogger(__name__)


def test_using_regex_from_structure():
    # Given
    expected_using = a_using_regex(selector="selector", ignore_case=True)
    structure = expected_using.as_structure()

    # When
    actual = Using.from_structure(structure)

    # Then
    assert actual.selector == "selector"
    assert actual.ignore_case is True


def test_using_xpath_from_structure():
    # Given
    expected_using = a_using_xpath(selector="selector", ns="ns")
    structure = expected_using.as_structure()

    # When
    actual = Using.from_structure(structure)

    # Then
    assert actual.selector == "selector"
    assert actual.ns == "ns"


def test_using_xpath_from_structure_no_ns():
    # Given
    expected_using = a_using_xpath(selector="selector", ns=None)
    structure = expected_using.as_structure()

    # When
    actual = Using.from_structure(structure)

    # Then
    assert actual.selector == "selector"
    assert actual.ns is None


def test_using_jsonpath_from_structure():
    # Given
    expected_using = a_using_jsonpath(selector="selector")
    structure = expected_using.as_structure()

    # When
    actual = Using.from_structure(structure)

    # Then
    assert actual.selector == "selector"
