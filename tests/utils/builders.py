# encoding=utf-8
from __future__ import unicode_literals, absolute_import, division, print_function

import email
import random
import string
from email.mime.text import MIMEText


def message(to_name=None, to_email=None, from_name=None, from_email=None, subject=None, body_text=None):
    to_name = to_name or random_string()
    to_email = to_email or random_email()
    from_name = from_name or random_string()
    from_email = from_email or random_email()
    subject = subject or random_string()
    body_text = body_text or random_string()

    msg = MIMEText(body_text)
    msg["To"] = email.utils.formataddr((to_name, to_email))
    msg["From"] = email.utils.formataddr((from_name, from_email))
    msg["Subject"] = subject
    return msg


def random_email():
    return "{0}@example.com".format(random_string())


def random_string(length=10, characters=string.ascii_letters + string.digits):
    return "".join(random.choice(characters) for _ in range(length))
