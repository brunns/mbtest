# flake8: noqa
# pragma: no cover
import pytest

from mb import server


@pytest.fixture(scope="session")
def mock_server(request):
    return server.mock_server(request)
