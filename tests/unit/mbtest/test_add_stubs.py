import pytest
from brunns.matchers.object import has_identical_properties_to
from hamcrest import assert_that, instance_of

from mbtest.imposters.stubs import AddStub
from tests.utils.builders import StubBuilder


@pytest.mark.parametrize("index", [0, 1, None])
def test_add_stubs_index(index):
    stub = StubBuilder().build()
    add_stub_obj = AddStub(stub=stub, index=index)
    structure = add_stub_obj.as_structure()
    assert structure.get("index") == index


def test_add_stubs_without_stub():
    # Given
    add_stub_obj = AddStub()
    structure = add_stub_obj.as_structure()

    # When
    actual = AddStub.from_structure(structure)

    assert_that(actual, instance_of(AddStub))
    assert_that(actual, has_identical_properties_to(add_stub_obj))
