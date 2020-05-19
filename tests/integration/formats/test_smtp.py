# encoding=utf-8
import email
import logging
import smtplib
from random import randint

from brunns.builder import a_string
from brunns.builder.email import EmailBuilder, EmailMessageBuilder
from hamcrest import assert_that
from mbtest.imposters import smtp_imposter
from mbtest.matchers import email_sent

logger = logging.getLogger(__name__)


def test_email(mock_server):
    # Given
    imposter = smtp_imposter()

    # TODO - make brunns-builders more realistic, so we don't have to do this here.'
    to_email = email.utils.formataddr(
        ((" ".join(a_string() for _ in range(randint(1, 3)))), (EmailBuilder().build()))
    )
    from_email = ", ".join(
        email.utils.formataddr(
            ((" ".join(a_string() for _ in range(randint(1, 3)))), EmailBuilder().build())
        )
        for _ in range(randint(1, 5))
    )
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
        assert_that(imposter, email_sent(body_text=body_text))
