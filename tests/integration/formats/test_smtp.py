# encoding=utf-8
import logging
import smtplib

from hamcrest import assert_that

from mbtest.imposters import smtp_imposter
from mbtest.matchers import email_sent
from tests.utils.builders import a_message, an_email, a_string

logger = logging.getLogger(__name__)


def test_email(mock_server):
    # Given
    imposter = smtp_imposter()

    to_email = an_email()
    from_email = an_email()
    body_text = a_string()

    with mock_server(imposter) as s:
        logger.debug("server: %s", s)

        # When
        server = smtplib.SMTP()
        server.connect(host=imposter.host, port=imposter.port)
        try:
            server.sendmail(
                to_email,
                [from_email],
                a_message(
                    to_email=to_email, from_email=from_email, body_text=body_text
                ).as_string(),
            )
        finally:
            server.quit()

        # Then
        assert_that(s, email_sent(body_text=body_text))
