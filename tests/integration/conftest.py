# encoding=utf-8
from __future__ import unicode_literals, absolute_import, division, print_function

import pytest

from mbtest import server


@pytest.fixture(scope="session")
def mock_server(request):
    return server.mock_server(request)
