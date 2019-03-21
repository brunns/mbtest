# encoding=utf-8
import logging
import socket

from hamcrest import assert_that, is_
from mbtest.imposters import Imposter, Stub, TcpPredicate, TcpResponse

logger = logging.getLogger(__name__)


def test_tcp(mock_server):
    imposter = Imposter(
        Stub(TcpPredicate(data="request"), TcpResponse(data="*" * 1024)),
        protocol=Imposter.Protocol.TCP,
    )

    with mock_server(imposter):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((imposter.host, imposter.port))
        client.send(b"request")

        response = client.recv(1024)

        assert_that(response, is_(b"*" * 1024))
