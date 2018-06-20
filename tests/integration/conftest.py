# flake8: noqa
# pragma: no cover
import os
import pytest

from mb import server


@pytest.fixture(scope="session")
def mock_server(request):
    os.environ["JIRA_USR"] = "foo"
    os.environ["JIRA_PSW"] = "bar"
    os.environ["AWS_DEFAULT_REGION"] = "eu-west-1"
    return server.mock_server(request)
