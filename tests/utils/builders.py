# encoding=utf-8

from brunns.builder import Builder, one_of, a_string, a_boolean

from mbtest.imposters import Copy, UsingRegex, UsingJsonpath, UsingXpath, Predicate


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
    using = UsingRegexBuilder
