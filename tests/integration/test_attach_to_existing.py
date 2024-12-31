import logging

import httpx
from brunns.matchers.response import is_response
from hamcrest import assert_that

from mbtest.imposters import Imposter, Predicate, Response, Stub
from mbtest.server import MountebankServer

logger = logging.getLogger(__name__)


def test_attach_to_existing(mock_server):
    imposter = Imposter(Stub(Predicate(path="/test"), Response(body="sausages")))
    with MountebankServer(port=mock_server.server_port)(imposter):
        response = httpx.get(f"{imposter.url}/test")

        assert_that(response, is_response().with_status_code(200).and_body("sausages"))
