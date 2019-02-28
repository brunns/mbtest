# encoding=utf-8
import logging

from mbtest.imposters import Lookup, Key, UsingJsonpath

logger = logging.getLogger(__name__)


def test_as_structure():
    # Given
    expected = Lookup(
        Key("from", UsingJsonpath(selector="selector"), index=2),
        "datasource_path",
        "datasource_key_column",
        "into",
    )
    structure = expected.as_structure()

    # When
    actual = Lookup.from_structure(structure)

    # Then
    assert actual.key.from_ == "from"
    assert actual.key.using.selector == "selector"
    assert actual.key.index == 2
    assert actual.datasource_path == "datasource_path"
    assert actual.datasource_key_column == "datasource_key_column"
    assert actual.into == "into"
