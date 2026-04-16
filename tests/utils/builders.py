import http
import random
from email.message import EmailMessage

from faker import Faker
from polyfactory import Use
from polyfactory.factories.dataclass_factory import DataclassFactory
from yarl import URL

from mbtest.imposters import (
    Copy,
    Imposter,
    InjectionResponse,
    Key,
    Lookup,
    Predicate,
    Proxy,
    Response,
    Stub,
    TcpResponse,
    UsingJsonpath,
    UsingRegex,
    UsingXpath,
)
from mbtest.imposters.imposters import Address, HttpRequest, SentEmail
from mbtest.imposters.predicates import (
    AndPredicate,
    InjectionPredicate,
    NotPredicate,
    OrPredicate,
    TcpPredicate,
)
from mbtest.imposters.responses import FaultResponse, HttpResponse

fake = Faker()


class UsingRegexFactory(DataclassFactory[UsingRegex]): ...


class UsingXpathFactory(DataclassFactory[UsingXpath]):
    ns = Use(lambda: None)


class UsingJsonpathFactory(DataclassFactory[UsingJsonpath]): ...


def _random_using():
    return random.choice([UsingRegexFactory.build(), UsingXpathFactory.build(), UsingJsonpathFactory.build()])


class CopyFactory(DataclassFactory[Copy]):
    from_ = Use(fake.word)
    using = Use(_random_using)


class TcpPredicateFactory(DataclassFactory[TcpPredicate]): ...


class InjectionPredicateFactory(DataclassFactory[InjectionPredicate]): ...


class KeyFactory(DataclassFactory[Key]):
    using = Use(_random_using)
    index = Use(lambda: random.randint(0, 50))


class LookupFactory(DataclassFactory[Lookup]):
    key = Use(KeyFactory.build)
    datasource_path = Use(str)  # from_structure always returns str, so keep consistent


class PredicateFactory(DataclassFactory[Predicate]):
    body = Use(lambda: random.choice([None, fake.word()]))


class AndPredicateFactory(DataclassFactory[AndPredicate]):
    left = Use(PredicateFactory.build)
    right = Use(PredicateFactory.build)


class OrPredicateFactory(DataclassFactory[OrPredicate]):
    left = Use(PredicateFactory.build)
    right = Use(PredicateFactory.build)


class NotPredicateFactory(DataclassFactory[NotPredicate]):
    inverted = Use(PredicateFactory.build)


class TcpResponseFactory(DataclassFactory[TcpResponse]): ...


class HttpResponseFactory(DataclassFactory[HttpResponse]):
    body = Use(str)
    status_code = Use(lambda: random.choice(list(http.HTTPStatus)))


class FaultResponseFactory(DataclassFactory[FaultResponse]): ...


class InjectionResponseFactory(DataclassFactory[InjectionResponse]): ...


class ResponseFactory(DataclassFactory[Response]):
    http_response = Use(HttpResponseFactory.build)
    copy = Use(lambda: random.choice([None, CopyFactory.build()]))
    lookup = Use(lambda: random.choice([None, LookupFactory.build()]))


class StubFactory(DataclassFactory[Stub]):
    predicates = Use(lambda: [PredicateFactory.build(), PredicateFactory.build()])
    responses = Use(lambda: [ResponseFactory.build(), ResponseFactory.build()])


class ProxyFactory(DataclassFactory[Proxy]):
    to = Use(lambda: URL("http://example.com"))
    predicate_generators = Use(list)


class AddressFactory(DataclassFactory[Address]): ...


class HttpRequestFactory(DataclassFactory[HttpRequest]):
    method = Use(lambda: random.choice(list(Predicate.Method)).name)
    query = Use(dict)
    headers = Use(dict)


class SentEmailFactory(DataclassFactory[SentEmail]):
    from_ = Use(AddressFactory.build)
    to = Use(lambda: [AddressFactory.build(), AddressFactory.build()])
    cc = Use(lambda: [AddressFactory.build(), AddressFactory.build()])
    bcc = Use(lambda: [AddressFactory.build(), AddressFactory.build()])


class ImposterFactory(DataclassFactory[Imposter]):
    stubs = Use(lambda: [StubFactory.build(), StubFactory.build()])
    port = Use(lambda: random.choice([None, random.randint(1, 5000)]))
    protocol = Use(lambda: random.choice(list(Imposter.Protocol)))
    name = Use(lambda: random.choice([None, "test"]))
    default_response = Use(lambda: random.choice([None, HttpResponseFactory.build()]))
    key = Use(lambda: None)
    cert = Use(lambda: None)
    host = Use(lambda: None)
    server_url = Use(lambda: None)


class EmailMessageFactory:
    @classmethod
    def build(
        cls,
        *,
        from_email: str | None = None,
        to_email: str | None = None,
        body_text: str | None = None,
    ) -> EmailMessage:
        msg = EmailMessage()
        msg["From"] = from_email or fake.email()
        msg["To"] = to_email or fake.email()
        msg.set_content(body_text or fake.sentence())
        return msg
