import os
import platform

import httpx
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
        port = docker_services.port_for("httpbin", 80)
        url = URL(f"http://{docker_ip}:{port}")
        docker_services.wait_until_responsive(timeout=30.0, pause=0.1, check=lambda: is_responsive(url))
        return url
    return URL("https://httpbin.org")


def is_responsive(url: URL) -> bool:
    try:
        response = httpx.get(str(url))
        response.raise_for_status()
    except httpx.HTTPError:
        return False
    else:
        return True
