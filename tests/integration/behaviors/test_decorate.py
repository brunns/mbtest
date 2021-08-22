# encoding=utf-8
import logging

import requests
from brunns.matchers.response import is_response
from hamcrest import assert_that

from mbtest.imposters import Imposter, Response, Stub

logger = logging.getLogger(__name__)

JS = """\
(request, response) => {
    response.body = response.body.replace('${NAME}', 'World');
}
"""


def test_decorate(mock_server):
    imposter = Imposter(Stub(responses=Response(body="Hello ${NAME}.", decorate=JS)))

    with mock_server(imposter):
        response = requests.get(imposter.url)

        assert_that(response, is_response().with_body("Hello World."))
