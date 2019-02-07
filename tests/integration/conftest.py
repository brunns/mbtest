# encoding=utf-8
import pytest

from mbtest import server


@pytest.fixture(scope="session")
def mock_server(request):
    return server.mock_server(request)
