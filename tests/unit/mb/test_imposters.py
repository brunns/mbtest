from hamcrest import assert_that, has_entries

from mb.imposters import Predicate


def test_default_predicate():
    # Given
    predicate = Predicate()

    # When
    structure = predicate.as_structure()

    # Then
    assert_that(structure, has_entries(caseSensitive=True, equals=has_entries(path="/", method="GET")))
