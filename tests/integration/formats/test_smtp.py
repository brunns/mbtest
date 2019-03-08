# encoding=utf-8
import logging
import smtplib

from brunns.builder import a_string
from brunns.builder.email import EmailMessageBuilder, EmailBuilder
from hamcrest import assert_that

from mbtest.imposters import smtp_imposter
from mbtest.matchers import email_sent

logger = logging.getLogger(__name__)


def test_email(mock_server):
    # Given
    imposter = smtp_imposter()

    to_email = EmailBuilder().build()
    from_email = EmailBuilder().build()
    body_text = a_string()
    message = (
        EmailMessageBuilder()
        .with_to_email(to_email)
        .with_from_email(from_email)
        .with_body_text(body_text)
        .build()
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
