# encoding=utf-8
import email
import random
import string
from email.mime.text import MIMEText

from mbtest.imposters import Copy, UsingRegex, UsingJsonpath, UsingXpath

NOT_PASSED = object()


def a_string(length=10, characters=string.ascii_letters + string.digits):
    return "".join(random.choice(characters) for _ in range(length))


def a_boolean():
    return random.choice([True, False])


def a_message(
    to_name=None, to_email=None, from_name=None, from_email=None, subject=None, body_text=None
):
    to_name = to_name or a_string()
    to_email = to_email or an_email()
    from_name = from_name or a_string()
    from_email = from_email or an_email()
    subject = subject or a_string()
    body_text = body_text or a_string()

    msg = MIMEText(body_text)
    msg["To"] = email.utils.formataddr((to_name, to_email))
    msg["From"] = email.utils.formataddr((from_name, from_email))
    msg["Subject"] = subject
    return msg


def an_email(user=None, domain=None):
    user = user or a_string()
    domain = domain or "example.com"
    return "{0}@{1}".format(user, domain)


def a_copy(from_=None, into=None, using=None):
    from_ = from_ or a_string()
    into = into or a_string()
    using = using or a_using()
    return Copy(from_, into, using)


def a_using(selector=None):
    selector = selector or a_string()
    return {
        1: a_using_regex(selector=selector),
        2: a_using_xpath(selector=selector),
        3: a_using_jsonpath(selector=selector),
    }[random.randint(1, 3)]


def a_using_regex(selector=None, ignore_case=NOT_PASSED):
    selector = selector or a_string()
    ignore_case = ignore_case if ignore_case != NOT_PASSED else a_boolean()
    return UsingRegex(selector, ignore_case=ignore_case)


def a_using_xpath(selector=None, ns=NOT_PASSED):
    ns = ns if ns != NOT_PASSED else random.choice([None, a_string()])
    selector = selector or a_string()
    return UsingXpath(selector=selector, ns=ns)


def a_using_jsonpath(selector=None):
    selector = selector or a_string()
    return UsingJsonpath(selector=selector)
