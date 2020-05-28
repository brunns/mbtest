# encoding=utf-8
import logging
import os

import pytest
from mbtest import server
from mbtest.server import MountebankServer

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def mock_server(request):
    if "DOCKER_MB_PORT" in os.environ:
        logger.info("Attaching to existing MB server on port %s", os.environ["DOCKER_MB_PORT"])
        return MountebankServer(
            host=os.environ.get("DOCKER_MB_HOST", "localhost"),
            port=int(os.environ["DOCKER_MB_PORT"]),
        )
    else:
        return server.mock_server(request)
