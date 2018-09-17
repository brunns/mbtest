# encoding=utf-8
from __future__ import unicode_literals, absolute_import, division, print_function

from hamcrest import assert_that, has_entries

from mbtest.imposters import Predicate


def test_default_predicate():
    # Given
    predicate = Predicate()

    # When
    structure = predicate.as_structure()

    # Then
    assert_that(structure, has_entries(caseSensitive=True, equals=has_entries()))
