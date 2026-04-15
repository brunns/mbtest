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


class UsingXpathFactory(DataclassFactory[UsingXpath]): ...


class UsingJsonpathFactory(DataclassFactory[UsingJsonpath]): ...


def _random_using():
    return random.choice([UsingRegexFactory.build(), UsingXpathFactory.build(), UsingJsonpathFactory.build()])  # noqa: S311


class CopyFactory(DataclassFactory[Copy]):
    using = Use(_random_using)


class TcpPredicateFactory(DataclassFactory[TcpPredicate]): ...


class InjectionPredicateFactory(DataclassFactory[InjectionPredicate]): ...


class KeyFactory(DataclassFactory[Key]):
    using = Use(_random_using)
    index = Use(lambda: random.randint(0, 50))  # noqa: S311


class LookupFactory(DataclassFactory[Lookup]):
    key = Use(KeyFactory.build)
    datasource_path = Use(str)  # from_structure always returns str, so keep consistent


class PredicateFactory(DataclassFactory[Predicate]): ...


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
    status_code = Use(lambda: random.choice(list(http.HTTPStatus)))  # noqa: S311


class FaultResponseFactory(DataclassFactory[FaultResponse]): ...


class InjectionResponseFactory(DataclassFactory[InjectionResponse]): ...


class ResponseFactory(DataclassFactory[Response]):
    http_response = Use(HttpResponseFactory.build)
    copy = Use(lambda: random.choice([None, CopyFactory.build()]))  # noqa: S311
    lookup = Use(lambda: random.choice([None, LookupFactory.build()]))  # noqa: S311


class StubFactory(DataclassFactory[Stub]):
    predicates = Use(lambda: [PredicateFactory.build(), PredicateFactory.build()])
    responses = Use(lambda: [ResponseFactory.build(), ResponseFactory.build()])


class ProxyFactory(DataclassFactory[Proxy]):
    to = Use(lambda: URL("http://example.com"))
    predicate_generators = Use(list)


class AddressFactory(DataclassFactory[Address]): ...


class HttpRequestFactory(DataclassFactory[HttpRequest]):
    method = Use(lambda: random.choice(list(Predicate.Method)).name)  # noqa: S311
    query = Use(dict)
    headers = Use(dict)


class SentEmailFactory(DataclassFactory[SentEmail]):
    from_ = Use(lambda: [AddressFactory.build()])
    to = Use(lambda: [AddressFactory.build(), AddressFactory.build()])
    cc = Use(lambda: [AddressFactory.build(), AddressFactory.build()])
    bcc = Use(lambda: [AddressFactory.build(), AddressFactory.build()])


class ImposterFactory(DataclassFactory[Imposter]):
    stubs = Use(lambda: [StubFactory.build(), StubFactory.build()])
    port = Use(lambda: random.choice([None, random.randint(1, 5000)]))  # noqa: S311
    protocol = Use(lambda: random.choice(list(Imposter.Protocol)))  # noqa: S311
    name = Use(lambda: random.choice([None, "test"]))  # noqa: S311
    default_response = Use(lambda: random.choice([None, HttpResponseFactory.build()]))  # noqa: S311
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
