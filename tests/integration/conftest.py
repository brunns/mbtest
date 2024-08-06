# encoding=utf-8
import os
import platform
from urllib.error import HTTPError

import pytest
import requests
from requests.exceptions import ConnectionError as RequestsConnectionError
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
        docker_services.wait_until_responsive(
            timeout=30.0, pause=0.1, check=lambda: is_responsive(url)
        )
        return url
    else:
        return URL("https://httpbin.org")


def is_responsive(url: URL) -> bool:
    try:
        response = requests.get(url)
        response.raise_for_status()
        return True
    except (RequestsConnectionError, HTTPError):
        return False
