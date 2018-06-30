from hamcrest import assert_that, not_, has_string

from matchers.matcher import mismatches_with
from matchers.smtp import email_with
from tests.utils.builders import message


def test_email_matcher():
    # Given
    m = message(to_name="fred", subject="chips", body_text="bananas").as_string()

    # When

    # Then
    assert_that(m, email_with(to_name="fred"))
    assert_that(m, not_(email_with(to_name="Banana")))
    assert_that(
        email_with(body_text="Foobar"), has_string("email with to_name ANYTHING subject ANYTHING body_text 'Foobar'")
    )
    assert_that(
        email_with(to_name="Banana"), mismatches_with(m, "was to_name 'fred' subject 'chips' body_text 'bananas'")
    )
