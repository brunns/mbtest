# encoding=utf-8
import http

from brunns.builder import Builder, a_boolean, a_string, an_integer, one_of
from brunns.builder.email import EmailAddressBuilder
from brunns.builder.internet import UrlBuilder

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
from mbtest.imposters.responses import HttpResponse


class PredicateBuilder(Builder):
    target = Predicate

    path = lambda: one_of(None, a_string())
    method = lambda: one_of(*Predicate.Method)
    query = lambda: one_of(None, {a_string(): a_string()})
    body = lambda: one_of(None, a_string())
    headers = lambda: one_of(None, {a_string(): a_string()})
    xpath = lambda: one_of(None, a_string())
    operator = lambda: one_of(*list(Predicate.Operator))
    case_sensitive = a_boolean


class AndPredicateBuilder(Builder):
    target = AndPredicate

    left = PredicateBuilder
    right = PredicateBuilder


class OrPredicateBuilder(Builder):
    target = OrPredicate

    left = PredicateBuilder
    right = PredicateBuilder


class NotPredicateBuilder(Builder):
    target = NotPredicate

    inverted = PredicateBuilder


class TcpResponseBuilder(Builder):
    target = TcpResponse

    data = a_string


class UsingRegexBuilder(Builder):
    target = UsingRegex

    selector = a_string
    ignore_case = a_boolean


class UsingXpathBuilder(Builder):
    target = UsingXpath

    selector = a_string
    ns = a_string


class UsingJsonpathBuilder(Builder):
    target = UsingJsonpath

    selector = a_string


class CopyBuilder(Builder):
    target = Copy

    from_ = a_string
    into = a_string
    using = lambda: one_of(
        UsingRegexBuilder().build(), UsingXpathBuilder().build(), UsingJsonpathBuilder().build()
    )


class TcpPredicateBuilder(Builder):
    target = TcpPredicate

    data = a_string


class InjectionPredicateBuilder(Builder):
    target = InjectionPredicate
    inject = a_string()


class KeyBuilder(Builder):
    target = Key

    from_ = a_string
    using = lambda: one_of(
        UsingRegexBuilder().build(), UsingXpathBuilder().build(), UsingJsonpathBuilder().build()
    )
    index = lambda: an_integer(1, 50)


class LookupBuilder(Builder):
    target = Lookup

    key = KeyBuilder
    datasource_path = a_string
    datasource_key_column = a_string
    into = a_string


class HttpResponseBuilder(Builder):
    target = HttpResponse

    body = a_string
    status_code = lambda: one_of(*[s.value for s in http.HTTPStatus])
    headers = lambda: one_of(None, {a_string(): a_string()})
    mode = lambda: one_of(*Response.Mode)


class ResponseBuilder(Builder):
    target = Response

    wait = lambda: one_of(an_integer(1, 500), None)
    repeat = lambda: one_of(an_integer(2, 50), None)
    copy = lambda: one_of(None, CopyBuilder().build())
    decorate = lambda: one_of(None, a_string())
    lookup = lambda: one_of(None, LookupBuilder().build())
    shell_transform = lambda: one_of(None, a_string())
    http_response = HttpResponseBuilder


class InjectionResponseBuilder(Builder):
    target = InjectionResponse
    inject = a_string()


class StubBuilder(Builder):
    target = Stub

    predicates = lambda: [PredicateBuilder().build(), PredicateBuilder().build()]
    responses = lambda: [ResponseBuilder().build(), ResponseBuilder().build()]


class ProxyBuilder(Builder):
    target = Proxy

    to = UrlBuilder
    wait = lambda: one_of(None, an_integer(1, 1000))
    inject_headers = lambda: one_of(None, {a_string(): a_string()})
    mode = lambda: one_of(*Proxy.Mode)
    decorate = lambda: one_of(None, a_string())


class ImposterBuilder(Builder):
    target = Imposter

    stubs = lambda: [StubBuilder().build(), StubBuilder().build()]
    port = lambda: one_of(None, an_integer(1, 5000))
    protocol = one_of(*Imposter.Protocol)
    name = lambda: one_of(None, a_string())
    default_response = lambda: one_of(None, HttpResponseBuilder().build())
    record_requests = a_boolean
    mutual_auth = a_boolean
    key = lambda: one_of(None, a_string())
    cert = lambda: one_of(None, a_string())


class HttpRequestBuilder(Builder):
    target = HttpRequest

    method = lambda: one_of(*Predicate.Method).name
    path = lambda: UrlBuilder().build().path
    query = lambda: {a_string(): a_string(), a_string(): a_string()}
    headers = lambda: {a_string(): a_string(), a_string(): a_string()}
    body = lambda: one_of(None, a_string())


class AddressBuilder(Builder):
    target = Address

    address = EmailAddressBuilder
    name = a_string


class SentEmailBuilder(Builder):
    target = SentEmail

    from_ = lambda: [AddressBuilder().build()]
    to = lambda: [AddressBuilder().build(), AddressBuilder().build()]
    cc = lambda: [AddressBuilder().build(), AddressBuilder().build()]
    bcc = lambda: [AddressBuilder().build(), AddressBuilder().build()]
    subject = a_string
    text = a_string
