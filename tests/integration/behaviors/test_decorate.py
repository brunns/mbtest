import logging

import httpx
from brunns.matchers.response import is_response
from hamcrest import assert_that

from mbtest.imposters import Imposter, Proxy, Response, Stub

logger = logging.getLogger(__name__)

JS = """\
(request, response) => {
    response.body = response.body.replace('${NAME}', 'World');
}
"""

JS_FOR_BINARY = """\
(request, response) => {
    var from_base64 = function (input) { return Buffer.from(input, 'base64').toString('utf-8') };
    var to_base64 = function (input) { return Buffer.from(input, 'utf-8').toString('base64') };

    response.body = to_base64(from_base64(response.body).replace('${NAME}', 'World'));
}
"""


def test_decorate_response(mock_server):
    imposter = Imposter(Stub(responses=Response(body="Hello ${NAME}.", decorate=JS)))

    with mock_server(imposter):
        response = httpx.get(str(imposter.url))

        assert_that(response, is_response().with_body("Hello World."))


def test_decorate_proxy(mock_server):
    proxy_target = Imposter(Stub(responses=Response(body="Hello ${NAME}.")))
    mock_server.add_impostor(proxy_target)

    imposter = Imposter(Stub(responses=Proxy(to=proxy_target.url, decorate=JS)))

    with mock_server(imposter):
        response = httpx.get(str(imposter.url))

        assert_that(response, is_response().with_body("Hello World."))


def test_decorate_proxy_binary(mock_server):
    proxy_target = Imposter(
        Stub(
            responses=Response(
                headers={"Content-Type": "application/octet-stream"},
                body="Hello ${NAME}.",
            )
        )
    )
    mock_server.add_impostor(proxy_target)

    imposter = Imposter(Stub(responses=Proxy(to=proxy_target.url, decorate=JS_FOR_BINARY)))

    with mock_server(imposter):
        response = httpx.get(str(imposter.url))

        assert_that(response, is_response().with_body("Hello World."))
