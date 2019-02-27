# encoding=utf-8
import logging
import platform
import subprocess  # nosec
import time
from collections.abc import Sequence
from pathlib import Path
from threading import Lock

import requests
from furl import furl
from requests import RequestException

DEFAULT_MB_EXECUTABLE = str(Path("node_modules") / ".bin" / ("mb.cmd" if platform.system() == "Windows" else "mb"))

logger = logging.getLogger(__name__)


class MountebankException(Exception):
    pass


class MountebankTimeoutError(MountebankException):
    pass


class MountebankServer:
    running = set()
    start_lock = Lock()

    def __init__(self, executable=DEFAULT_MB_EXECUTABLE, port=2525, timeout=5):
        self.server_port = port
        self.running_imposters_by_port = {}
        with self.start_lock:
            if self.server_port in self.running:
                raise MountebankException("Already running on port {0}.".format(self.server_port))
            try:
                self.mb_process = subprocess.Popen([executable, "--port", str(port), "--debug"])  # nosec
                self._await_start(timeout)
                self.running.add(port)
                logger.info("Spawned mb process %s on port %s.", self.mb_process.pid, self.server_port)
            except OSError:
                logger.error(
                    "Failed to spawn mb process with executable at %s. Have you installed Mountebank?", executable
                )
                raise

    def __call__(self, imposters):
        self.imposters = imposters
        return self

    def __enter__(self):
        self.add_imposters(self.imposters)
        return self

    def __exit__(self, ex_type, ex_value, ex_traceback):
        self.delete_imposters()

    def _await_start(self, timeout):
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                requests.get(self.server_url, timeout=1).raise_for_status()
                started = True
                break
            except RequestException:
                started = False
                time.sleep(0.1)

        if not started:
            raise MountebankTimeoutError("Mountebank failed to start within {0} seconds.".format(timeout))

        logger.debug("Server started at %s.", self.server_url)

    def add_imposters(self, definition):
        """Add imposters to Mountebank server.

        :param definition: One or more Imposters.
        :type definition: Imposter or list(Imposter)
        """
        if isinstance(definition, Sequence):
            for imposter in definition:
                self.add_imposters(imposter)
        else:
            json = definition.as_structure()
            post = requests.post(self.server_url, json=json, timeout=10)
            post.raise_for_status()
            definition.port = post.json()["port"]
            self.running_imposters_by_port[definition.port] = definition

    def delete_imposters(self):
        while self.running_imposters_by_port:
            imposter_port, imposter = self.running_imposters_by_port.popitem()
            requests.delete(self.imposter_url(imposter_port)).raise_for_status()

    def get_actual_requests(self):
        impostors = {}
        for imposter_port in self.running_imposters_by_port:
            response = requests.get(self.imposter_url(imposter_port), timeout=5)
            response.raise_for_status()
            json = response.json()
            impostors[imposter_port] = json["requests"]
        return impostors

    @property
    def server_url(self):
        return furl().set(scheme="http", host="localhost", port=self.server_port, path="imposters")

    def imposter_url(self, imposter_port):
        return self.server_url.add(path=str(imposter_port))

    def close(self):
        self.mb_process.terminate()
        self.mb_process.wait()
        self.running.remove(self.server_port)
        logger.info(
            "Terminated mb process %s on port %s status %s.",
            self.mb_process.pid,
            self.server_port,
            self.mb_process.returncode,
        )


def mock_server(request, executable=DEFAULT_MB_EXECUTABLE, port=2525, **kwargs):
    """A mock server, running one or more impostors, one for each site being mocked.

    Use in a pytest conftest.py fixture as follows:

    @pytest.fixture(scope="session")
    def mock_server(request):
        return server.mock_server(request)

    Test will look like:

    def test_1_imposter(mock_server):
        imposter = Imposter(Stub(Predicate(path='/test'),
                                 Response(body='sausages')),
                            record_requests=True)

        with mock_server(imposter) as s:
            r = requests.get('{0}/test'.format(imposter.url))

            assert_that(r, is_(response_with(status_code=200, body="sausages")))
            assert_that(s, had_request(path='/test', method="GET"))

    This function can take optional keyword arguments:

    * timeout - specifies how long to wait for the Mountebank server to start.
    * port - Server port
    * executable - Alternate location for the Mountebank executable.
    """
    server = MountebankServer(executable=executable, port=port, **kwargs)

    def close():
        server.close()

    request.addfinalizer(close)

    return server
