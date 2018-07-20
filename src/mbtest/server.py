import collections
import logging
import subprocess  # nosec
import time

import requests
from furl import furl
from more_itertools import flatten

logger = logging.getLogger(__name__)


class MountebankException(Exception):
    pass


class TimeoutError(BaseException):
    pass


class MountebankServer(object):
    IMPOSTERS_URL = furl().set(scheme="http", host="localhost", port=2525, path="imposters").url

    def __init__(self):
        self.mb_process = subprocess.Popen(["./node_modules/.bin/mb", "--debug"], stdout=subprocess.PIPE)  # nosec
        self._await_start()
        logger.info("Spawned mb process.")

    def __call__(self, imposters):
        self.imposters = imposters

        return self

    def __enter__(self):
        self.ports = self.create_imposters(self.imposters)
        return self

    def __exit__(self, ex_type, ex_value, ex_traceback):
        self.delete_imposters()

    def _await_start(self, timeout=5):  # pragma: no cover
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                requests.get(self.IMPOSTERS_URL, timeout=1).raise_for_status()
                started = True
                break
            except Exception:
                started = False
                time.sleep(0.1)

        if not started:
            raise TimeoutError("Mountebank failed to start within the defined timeout")

    def create_imposters(self, definition):
        if isinstance(definition, collections.Sequence):
            return list(flatten(self.create_imposters(imposter) for imposter in definition))
        else:
            json = definition.as_structure()
            post = requests.post(self.IMPOSTERS_URL, json=json, timeout=10)
            post.raise_for_status()
            definition.port = post.json()["port"]
            return [definition.port]

    def delete_imposters(self):
        for port in self.ports:
            requests.delete(self.imposter_url(port))

    def get_actual_requests(self):
        impostors = {}
        for port in self.ports:
            response = requests.get(self.imposter_url(port), timeout=10)
            response.raise_for_status()
            json = response.json()
            impostors[port] = json["requests"]
        return impostors

    def imposter_url(self, port):
        return furl(self.IMPOSTERS_URL).add(path="{0}".format(port)).url

    def close(self):
        self.mb_process.terminate()


def mock_server(request):
    """A mock server, running one or more impostors, one for each site being mocked.

    Use in a pytest conftest.py fixture as follows:

    @pytest.fixture(scope="session")
    def mock_server(request):
        return server.mock_server(request)

    Test will look like:

    @pytest.mark.usefixtures("mock_server")
    def test_1_imposter(mock_server):
        imposter = Imposter(Stub(Predicate(path='/test'),
                                 Response(body='sausages')),
                            record_requests=True)

        with mock_server(imposter) as s:
            r = requests.get('{0}/test'.format(imposter.url))

            assert_that(r, is_(response_with(status_code=200, body="sausages")))
            assert_that(s, had_request(path='/test', method="GET"))
    """
    server = MountebankServer()

    def close():
        server.close()

    request.addfinalizer(close)

    return server
