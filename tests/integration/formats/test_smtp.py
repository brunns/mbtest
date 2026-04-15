import logging
import smtplib

from faker import Faker
from hamcrest import assert_that, has_item, has_properties

from mbtest.imposters import smtp_imposter
from mbtest.matchers import email_sent
from tests.utils.builders import EmailMessageFactory

logger = logging.getLogger(__name__)
fake = Faker()


def test_email(mock_server):
    # Given
    imposter = smtp_imposter()
    from_email = fake.email()
    to_email = fake.email()
    body_text = fake.sentence()
    msg = EmailMessageFactory.build(from_email=from_email, to_email=to_email, body_text=body_text)

    with mock_server(imposter) as s:
        logger.debug("server: %s", s)

        # When
        server = smtplib.SMTP()
        server.connect(host=imposter.host, port=imposter.port)
        try:
            server.sendmail(msg["From"], [msg["To"]], msg.as_string())
        finally:
            server.quit()

        # Then
        assert_that(
            imposter,
            email_sent()
            .with_from_(has_properties(address=from_email))
            .and_to(has_item(has_properties(address=to_email)))
            .and_body_text(body_text),
        )
