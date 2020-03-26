# encoding=utf-8
import logging

import requests
from brunns.matchers.response import is_response
from hamcrest import assert_that, matches_regexp
from mbtest.imposters import Imposter, Response, Stub

logger = logging.getLogger(__name__)

JS = """\
(request, response) => {
    var pad = function (number) { return (number < 10) ? '0' + number : number.toString(); },
    now = new Date(),
    time = pad(now.getHours()) + ':' + pad(now.getMinutes()) + ':' + pad(now.getSeconds());
    response.body = response.body.replace('${TIME}', time);
}
"""


def test_decorate(mock_server):
    imposter = Imposter(Stub(responses=Response(body="The time is ${TIME}.", decorate=JS)))

    with mock_server(imposter):
        response = requests.get(imposter.url)

        assert_that(
            response, is_response().with_body(matches_regexp(r"The time is \d\d:\d\d:\d\d\."))
        )
