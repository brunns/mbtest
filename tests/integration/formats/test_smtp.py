# encoding=utf-8
import logging
import smtplib

from hamcrest import assert_that

from mbtest.imposters import smtp_imposter
from mbtest.matchers import email_sent
from tests.utils.builders import a_string, an_email_address, email_message_builder

logger = logging.getLogger(__name__)


def test_email(mock_server):
    # Given
    imposter = smtp_imposter()

    to_email = an_email_address()
    from_email = an_email_address()
    body_text = a_string()
    message = (
        email_message_builder()
        .with_to_email(to_email)
        .with_from_email(from_email)
        .with_body_text(body_text)
        .as_string()
    )

    with mock_server(imposter) as s:
        logger.debug("server: %s", s)

        # When
        server = smtplib.SMTP()
        server.connect(host=imposter.host, port=imposter.port)
        try:
            server.sendmail(to_email, [from_email], message)
        finally:
            server.quit()

        # Then
        assert_that(s, email_sent(body_text=body_text))
