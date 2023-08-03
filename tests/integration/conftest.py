# encoding=utf-8
import sys

import pytest
from imurl.url import URL

from mbtest import server

WINDOWS = sys.platform.startswith("win")


@pytest.fixture(scope="session")
def mock_server(request):
    return server.mock_server(request)


@pytest.fixture(scope="session")
def httpbin(docker_ip, docker_services) -> URL:
    if WINDOWS:
        # We can't run docker inside a Windows VM in GitHub Actions, so run tests against the public instance.
        return URL("https://httpbin.org")
    else:
        docker_services.start("httpbin")
        port = docker_services.wait_for_service("httpbin", 80)
        return URL(f"http://{docker_ip}:{port}")
