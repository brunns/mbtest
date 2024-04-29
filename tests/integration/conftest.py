# encoding=utf-8
import os
import platform

import pytest
from yarl import URL

from mbtest import server

LOCAL = os.getenv("GITHUB_ACTIONS") != "true"
LINUX = platform.system() == "Linux"
HTTPBIN_CONTAINERISED = LINUX or LOCAL


@pytest.fixture(scope="session")
def mock_server(request):
    return server.mock_server(request)


@pytest.fixture(scope="session")
def httpbin(docker_ip, docker_services) -> URL:
    if HTTPBIN_CONTAINERISED:
        docker_services.start("httpbin")
        port = docker_services.wait_for_service("httpbin", 80)
        return URL(f"http://{docker_ip}:{port}")
    else:
        return URL("https://httpbin.org")
