import logging
import platform

import httpx
import pytest
from brunns.matchers.data import json_matching
from brunns.matchers.response import is_response
from hamcrest import assert_that

from mbtest.imposters import Imposter, Response, Stub

logger = logging.getLogger(__name__)

SCRIPT = """import sys, json
resp = json.loads(sys.argv[1])
body = json.loads(resp['body'])
body['person']['name'] = body['person']['name'].upper()
resp['body'] = json.dumps(body)
print(json.dumps(resp))
"""


@pytest.mark.skipif(platform.system() == "Windows", reason="TODO: Fix on Windows.")
def test_shell_transform(mock_server):
    imposter = Imposter(Stub(responses=Response(body="Hello ${name}!", shell_transform=f'python -c "{SCRIPT}" ')))

    with mock_server(imposter):
        response = httpx.post(str(imposter.url), json={"person": {"name": "Alice"}})

        assert_that(
            response,
            is_response().with_body(json_matching({"person": {"name": "ALICE"}})),
        )
