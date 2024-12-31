import logging

from mbtest.imposters import Copy
from tests.utils.builders import CopyBuilder, UsingRegexBuilder

logger = logging.getLogger(__name__)


def test_from_structure():
    # Given
    using = UsingRegexBuilder(selector="selector").build()
    expected_copy = CopyBuilder(from_="from", into="into", using=using)
    structure = expected_copy.as_structure()

    # When
    actual = Copy.from_structure(structure)

    # Then
    assert actual.from_ == "from"
    assert actual.into == "into"
    assert actual.using.selector == "selector"
