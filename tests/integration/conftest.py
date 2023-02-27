# encoding=utf-8
import sys

import pytest
from imurl import URL

from mbtest import server


@pytest.fixture(scope="session")
def mock_server(request):
    return server.mock_server(request)


@pytest.fixture(scope="session")
def httpbin(docker_ip, docker_services) -> URL:
    if not sys.platform.startswith("win"):
        docker_services.start("httpbin")
        port = docker_services.wait_for_service("httpbin", 80)
        return URL(f"http://{docker_ip}:{port}")
    return URL("https://httpbin.org")
