# encoding=utf-8
import abc
import email
import random
import string
from email.mime.text import MIMEText

from mbtest.imposters import Copy, UsingRegex, UsingJsonpath, UsingXpath, Predicate

NOT_PASSED = object()


def a_string(length=10, characters=string.ascii_letters + string.digits):
    return "".join(random.choice(characters) for _ in range(length))


def an_integer(a=None, b=None):
    return random.randint(a, b)


def a_boolean():
    return random.choice([True, False])


class TestObjectBuilder(metaclass=abc.ABCMeta):
    @property
    @abc.abstractmethod
    def value(self):
        raise NotImplementedError()

    def __getattr__(self, item):
        """Dynamic 'with_x' methods."""
        target = item.partition("with_")[2]
        if target:

            def with_(value):
                setattr(self, target, value)
                return self

            return with_
        else:
            return getattr(self.value, item)

    def __getitem__(self, item):
        return self.value[item]


def an_email_message():
    return email_message_builder().value


def email_message_builder():
    return EmailMessageBuilder()


class EmailMessageBuilder(TestObjectBuilder):
    def __init__(self):
        self.to_name = a_string()
        self.to_email_address = an_email_address()
        self.from_name = a_string()
        self.from_email_address = an_email_address()
        self.subject = a_string()
        self.body_text = a_string()

    @property
    def value(self):
        message = MIMEText(self.body_text)
        message["To"] = email.utils.formataddr((self.to_name, self.to_email_address))
        message["From"] = email.utils.formataddr((self.from_name, self.from_email_address))
        message["Subject"] = self.subject
        return message


def a_predicate(**kwargs):
    builder = predicate_builder()
    for key, value in kwargs.items():
        setattr(builder, key, value)
    return builder.value


def predicate_builder():
    return PredicateBuilder()


class PredicateBuilder(TestObjectBuilder):
    def __init__(self):
        self.path = random.choice([None, a_string()])
        self.method = random.choice(list(Predicate.Method))
        self.query = random.choice([None, {a_string(): a_string()}])
        self.body = random.choice([None, a_string()])
        self.headers = random.choice([None, {a_string(): a_string()}])
        self.xpath = random.choice([None, a_string()])
        self.operator = random.choice(list(Predicate.Operator))
        self.case_sensitive = a_boolean()

    @property
    def value(self):
        return Predicate(
            path=self.path,
            method=self.method,
            query=self.query,
            body=self.body,
            headers=self.headers,
            xpath=self.xpath,
            operator=self.operator,
            case_sensitive=self.case_sensitive,
        )


def a_domain():
    return domain_builder().value


def domain_builder():
    return DomainBuilder()


class DomainBuilder(TestObjectBuilder):
    def __init__(self):
        self.subdomain = a_string(characters=string.ascii_lowercase)
        self.tld = random.choice(["com", "net", "dev", "co.uk"])

    @property
    def value(self):
        return "{0}.{1}".format(self.subdomain, self.tld)


def an_email_address():
    return email_address_builder().value


def email_address_builder():
    return EmaiAddressBuilder()


class EmaiAddressBuilder(TestObjectBuilder):
    def __init__(self):
        self.username = a_string()
        self.domain = a_domain()

    @property
    def value(self):
        return "{0}@{1}".format(self.username, self.domain)


def a_copy(from_=None, into=None, using=None):
    builder = copy_builder()
    if from_:
        builder.with_from(from_)
    if into:
        builder.with_into(into)
    if using:
        builder.with_using(using)
    return builder.value


def copy_builder():
    return CopyBuilder()


class CopyBuilder(TestObjectBuilder):
    def __init__(self):
        self.from_ = a_string()
        self.into = a_string()
        self.using = a_using()

    def with_from(self, from_):
        self.from_ = from_

    @property
    def value(self):
        return Copy(self.from_, self.into, self.using)


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
