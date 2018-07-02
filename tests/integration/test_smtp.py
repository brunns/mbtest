import logging
import smtplib

import pytest
from hamcrest import assert_that

from mbtest.matchers import email_sent
from mbtest.imposters import smtp_imposter
from tests.utils.builders import message, random_email, random_string

logger = logging.getLogger(__name__)


@pytest.mark.usefixtures("mock_server")
def test_email(mock_server):
    # Given
    imposter = smtp_imposter()

    to_email = random_email()
    from_email = random_email()
    body_text = random_string()

    with mock_server(imposter) as s:
        logger.debug("server: %s", s)

        # When
        server = smtplib.SMTP()
        server.connect(host=imposter.host, port=imposter.port)
        try:
            server.sendmail(
                to_email,
                [from_email],
                message(to_email=to_email, from_email=from_email, body_text=body_text).as_string(),
            )
        finally:
            server.quit()

        # Then
        assert_that(s, email_sent(body_text=body_text))
