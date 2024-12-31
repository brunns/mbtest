import logging
import smtplib

from brunns.builder import a_string
from brunns.builder.email import EmailAddressBuilder, EmailMessageBuilder
from hamcrest import assert_that

from mbtest.imposters import smtp_imposter
from mbtest.matchers import email_sent

logger = logging.getLogger(__name__)


def test_email(mock_server):
    # Given
    imposter = smtp_imposter()

    from_email = EmailAddressBuilder().build()
    to_email = EmailAddressBuilder().build()
    body_text = a_string()

    message = EmailMessageBuilder().with_to(to_email).and_from(from_email).and_body_text(body_text).build().as_string()

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
