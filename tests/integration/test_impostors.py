# encoding=utf-8
import json
import logging
import os
from pathlib import Path

import pytest
import requests
import trustme
from brunns.matchers.data import json_matching
from brunns.matchers.response import is_response
from hamcrest import assert_that, contains_exactly, has_entries
from requests.exceptions import SSLError

from mbtest.imposters import Imposter, Predicate, Response, Stub
from mbtest.imposters.responses import HttpResponse
from mbtest.matchers import had_request

logger = logging.getLogger(__name__)


def test_multiple_imposters(mock_server):
    imposters = [
        Imposter(Stub(Predicate(path="/test1"), Response(body="sausages"))),
        Imposter([Stub([Predicate(path="/test2")], [Response(body="chips", status_code=201)])]),
    ]

    with mock_server(imposters):
        r1 = requests.get(f"{imposters[0].url}/test1")
        r2 = requests.get(f"{imposters[1].url}/test2")

    assert_that(r1, is_response().with_status_code(200).and_body("sausages"))
    assert_that(r2, is_response().with_status_code(201).and_body("chips"))


def test_default_imposter(mock_server):
    imposter = Imposter(Stub())

    with mock_server(imposter):
        r = requests.get(f"{imposter.url}/")

    assert_that(r, is_response().with_status_code(200).and_body(""))


def test_imposter_had_request_matcher(mock_server):
    imposter = Imposter(Stub(Predicate(path="/test"), Response(body="sausages")))

    with mock_server(imposter):
        response = requests.get(f"{imposter.url}/test")

        assert_that(response, is_response().with_status_code(200).and_body("sausages"))
        assert_that(imposter, had_request().with_path("/test").and_method("GET"))


@pytest.mark.skipif(
    float(os.environ.get("MBTEST_VERSION", "2.1")) < 2.1,
    reason="Adding stubs to existing imposter requires Mountebank version 2.1 or higher.",
)
def test_add_stub_to_running_impostor(mock_server):
    impostor = Imposter(
        Stub(Predicate(path="/test0"), Response(body="response0")),
        default_response=HttpResponse(body="default"),
    )

    with mock_server(impostor):

        responses = [requests.get(f"{impostor.url}/test{i}") for i in range(3)]
        assert_that(
            responses,
            contains_exactly(
                is_response().with_body("response0"),
                is_response().with_body("default"),
                is_response().with_body("default"),
            ),
        )

        index = impostor.add_stub(
            Stub(Predicate(path="/test1"), Response(body="response1")),
        )
        assert index == 1

        responses = [requests.get(f"{impostor.url}/test{i}") for i in range(3)]
        assert_that(
            responses,
            contains_exactly(
                is_response().with_body("response0"),
                is_response().with_body("response1"),
                is_response().with_body("default"),
            ),
        )


@pytest.mark.skipif(
    float(os.environ.get("MBTEST_VERSION", "2.1")) < 2.1,
    reason="Adding stubs to existing imposter requires Mountebank version 2.1 or higher.",
)
def test_add_stubs_to_running_impostor(mock_server):
    impostor = Imposter(
        Stub(Predicate(path="/test0"), Response(body="response0")),
        default_response=HttpResponse(body="default"),
    )

    with mock_server(impostor):

        responses = [requests.get(f"{impostor.url}/test{i}") for i in range(3)]
        assert_that(
            responses,
            contains_exactly(
                is_response().with_body("response0"),
                is_response().with_body("default"),
                is_response().with_body("default"),
            ),
        )

        impostor.add_stubs(
            [
                Stub(Predicate(path="/test1"), Response(body="response1")),
            ]
        )
        responses = [requests.get(f"{impostor.url}/test{i}") for i in range(3)]
        assert_that(
            responses,
            contains_exactly(
                is_response().with_body("response0"),
                is_response().with_body("response1"),
                is_response().with_body("default"),
            ),
        )


@pytest.mark.skipif(
    float(os.environ.get("MBTEST_VERSION", "2.1")) < 2.1,
    reason="Removing stubs from existing imposter requires Mountebank version 2.1 or higher.",
)
def test_remove_and_replace_stub_from_running_impostor(mock_server):
    impostor = Imposter(
        stubs=[
            Stub(Predicate(path="/test0"), Response(body="response0")),
            Stub(Predicate(path="/test1"), Response(body="response1")),
            Stub(Predicate(path="/test2"), Response(body="response2")),
        ],
        default_response=HttpResponse(body="default"),
    )

    with mock_server(impostor):
        responses = [requests.get(f"{impostor.url}/test{i}") for i in range(3)]
        assert_that(
            responses,
            contains_exactly(
                is_response().with_body("response0"),
                is_response().with_body("response1"),
                is_response().with_body("response2"),
            ),
        )

        impostor.delete_stub(1)

        responses = [requests.get(f"{impostor.url}/test{i}") for i in range(3)]
        assert_that(
            responses,
            contains_exactly(
                is_response().with_body("response0"),
                is_response().with_body("default"),
                is_response().with_body("response2"),
            ),
        )

        impostor.add_stub(Stub(Predicate(path="/test1"), Response(body="response1")))
        responses = [requests.get(f"{impostor.url}/test{i}") for i in range(3)]
        assert_that(
            responses,
            contains_exactly(
                is_response().with_body("response0"),
                is_response().with_body("response1"),
                is_response().with_body("response2"),
            ),
        )


def test_build_imposter_from_structure_on_disk(mock_server):
    # Given
    structure_path = Path("tests") / "integration" / "test_data" / "impostor_structure.json"

    # When
    with structure_path.open() as f:
        structure = json.load(f)
    imposter = Imposter.from_structure(structure["imposters"][0])

    with mock_server(imposter):
        response = requests.get(f"{imposter.url}/tutorial")

    # Then
    assert_that(
        response,
        is_response().with_status_code(200).and_body(json_matching(has_entries(message="success"))),
    )


def test_https_impostor_fails_if_cert_not_supplied(mock_server):
    imposter = Imposter(
        Stub(Predicate(path="/test"), Response(body="sausages")),
        protocol=Imposter.Protocol.HTTPS,
    )

    with mock_server(imposter):
        with pytest.raises(SSLError):
            requests.get(f"{imposter.url}/test")


def test_https_impostor_works_with_cert_supplied(mock_server):
    ca = trustme.CA()
    server_cert = ca.issue_cert("localhost")

    imposter = Imposter(
        Stub(Predicate(path="/test"), Response(body="sausages")),
        protocol=Imposter.Protocol.HTTPS,
        mutual_auth=True,
        key=server_cert.private_key_pem.bytes().decode("utf-8"),
        cert=server_cert.cert_chain_pems[0].bytes().decode("utf-8"),
    )

    with mock_server(imposter), ca.cert_pem.tempfile() as certfile:
        response = requests.get(f"{imposter.url}/test", verify=certfile)

    assert_that(response, is_response().with_status_code(200).and_body("sausages"))


def test_default_response(mock_server):
    imposter = Imposter(
        Stub(Predicate(path="/test1"), Response(body="sausages")),
        default_response=HttpResponse("chips", status_code=201),
    )

    with mock_server(imposter):
        r1 = requests.get(f"{imposter.url}/test1")
        r2 = requests.get(f"{imposter.url}/test2")

    assert_that(r1, is_response().with_status_code(200).and_body("sausages"))
    assert_that(r2, is_response().with_status_code(201).and_body("chips"))
