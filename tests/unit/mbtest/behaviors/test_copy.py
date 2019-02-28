# encoding=utf-8
import logging

from mbtest.imposters import Copy
from tests.utils.builders import a_copy, a_using

logger = logging.getLogger(__name__)


def test_from_structure():
    # Given
    expected_copy = a_copy(from_="from", into="into", using=a_using(selector="selector"))
    structure = expected_copy.as_structure()

    # When
    actual = Copy.from_structure(structure)

    # Then
    assert actual.from_ == "from"
    assert actual.into == "into"
    assert actual.using.selector == "selector"
