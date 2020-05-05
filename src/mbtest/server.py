# encoding=utf-8
import collections.abc as abc
import logging
import platform
import subprocess  # nosec
import time
from pathlib import Path
from threading import Lock
from typing import Iterable, List, Mapping, MutableMapping, Sequence, Set, Union, cast

import requests
from _pytest.fixtures import FixtureRequest  # type: ignore
from furl import furl
from mbtest.imposters import Imposter
from mbtest.imposters.base import JsonStructure
from requests import RequestException

DEFAULT_MB_EXECUTABLE = str(
    Path("node_modules") / ".bin" / ("mb.cmd" if platform.system() == "Windows" else "mb")
)

logger = logging.getLogger(__name__)


def mock_server(
    request: FixtureRequest,
    executable: Union[str, Path] = DEFAULT_MB_EXECUTABLE,
    port: int = 2525,
    timeout: int = 5,
    debug: bool = True,
    allow_injection: bool = True,
    local_only: bool = True,
    data_dir: Union[str, None] = ".mbdb",
) -> "ExecutingMountebankServer":
    """`Pytest fixture <https://docs.pytest.org/en/latest/fixture.html>`_, making available a mock server, running one
    or more impostors, one for each domain being mocked.

    Use in a pytest conftest.py fixture as follows::

        @pytest.fixture(scope="session")
        def mock_server(request):
            return server.mock_server(request)

    Test will look like::

        def test_an_imposter(mock_server):
            imposter = Imposter(Stub(Predicate(path='/test'),
                                     Response(body='sausages')),
                                record_requests=True)

            with mock_server(imposter) as s:
                r = requests.get('{0}/test'.format(imposter.url))

                assert_that(r, is_response().with_status_code(200).and_body("sausages"))
                assert_that(s, had_request(path='/test', method="GET"))

    :param request: Request for a fixture from a test or fixture function.
    :param executable: Alternate location for the Mountebank executable.
    :param port: Server port.
    :param timeout: specifies how long to wait for the Mountebank server to start.
    :param debug: Start the server in debug mode, which records all requests. This needs to be `True` for the
        :py:func:`mbtest.matchers.had_request` matcher to work.
    :param allow_injection: Allow JavaScript injection. If `True`, `local_only` should also be `True`,as per
        `Mountebank security <http://www.mbtest.org/docs/security>`_.
    :param local_only: Accept request only from localhost.
    :param data_dir: Persist all operations to disk, in this directory.

    :returns: Mock server.
    """
    server = ExecutingMountebankServer(
        executable=executable,
        port=port,
        timeout=timeout,
        debug=debug,
        allow_injection=allow_injection,
        local_only=local_only,
        data_dir=data_dir,
    )

    def close():
        server.close()

    request.addfinalizer(close)

    return server


class MountebankServer:
    """Allow addition of imposters to an already running Mountebank mock server.

    Test will look like::

        def test_an_imposter(mock_server):
            mb = MountebankServer(1234)
            imposter = Imposter(Stub(Predicate(path='/test'),
                                     Response(body='sausages')),
                                record_requests=True)

            with mb(imposter) as s:
                r = requests.get('{0}/test'.format(imposter.url))

                assert_that(r, is_response().with_status_code(200).and_body("sausages"))
                assert_that(s, had_request(path='/test', method="GET"))

    Impostors will be torn down when the `with` block is exited.

    :param port: Server port.
    :param scheme: Server scheme, if not `http`.
    :param host: Server host, if not `localhost`.
    :param imposters_path: Impostors path, if not `imposters`.

    """

    def __init__(
        self,
        port: int,
        scheme: str = "http",
        host: str = "localhost",
        imposters_path: str = "imposters",
    ):
        self.server_port = port
        self.host = host
        self.scheme = scheme
        self.imposters_path = imposters_path

    def __call__(self, imposters: Sequence[Imposter]) -> "MountebankServer":
        self.imposters = imposters
        self.running_imposters_by_port = {}  # type: MutableMapping[int, Imposter]
        return self

    def __enter__(self) -> "MountebankServer":
        self.add_imposters(self.imposters)
        return self

    def __exit__(self, ex_type, ex_value, ex_traceback) -> None:
        self.delete_imposters()

    def add_imposters(self, definition: Union[Imposter, Iterable[Imposter]]) -> None:
        """Add imposters to Mountebank server.

        :param definition: One or more Imposters.
        :type definition: Imposter or list(Imposter)
        """
        if isinstance(definition, abc.Iterable):
            for imposter in definition:
                self.add_imposters(imposter)
        else:
            json = definition.as_structure()
            post = requests.post(self.server_url, json=json, timeout=10)
            post.raise_for_status()
            definition.port = post.json()["port"]
            self.running_imposters_by_port[cast(int, definition.port)] = definition

    def delete_imposters(self) -> None:
        while self.running_imposters_by_port:
            imposter_port, imposter = self.running_imposters_by_port.popitem()
            requests.delete(self.imposter_url(imposter_port)).raise_for_status()

    def get_actual_requests(self) -> Mapping[int, JsonStructure]:
        requests_by_impostor = {}
        for imposter_port in self.running_imposters_by_port:
            response = requests.get(self.imposter_url(imposter_port), timeout=5)
            response.raise_for_status()
            json = response.json()
            requests_by_impostor[imposter_port] = json["requests"]
        return requests_by_impostor

    @property
    def server_url(self) -> furl:
        return furl().set(
            scheme=self.scheme, host=self.host, port=self.server_port, path=self.imposters_path
        )

    def imposter_url(self, imposter_port: int) -> furl:
        return self.server_url.add(path=str(imposter_port))


class ExecutingMountebankServer(MountebankServer):
    """A Mountebank mock server, running one or more impostors, one for each domain being mocked.

    Test will look like::

        def test_an_imposter(mock_server):
            mb = ExecutingMountebankServer()
            imposter = Imposter(Stub(Predicate(path='/test'),
                                     Response(body='sausages')),
                                record_requests=True)

            with mb(imposter) as s:
                r = requests.get('{0}/test'.format(imposter.url))

                assert_that(r, is_response().with_status_code(200).and_body("sausages"))
                assert_that(s, had_request(path='/test', method="GET"))

            mb.close()

    The mountebank server will be started when this class is instantiated, and needs to be closed if it's not to be
    left running. Consider using the :meth:`mock_server` pytest fixture, which will take care of this for you.

    :param executable: Optional, alternate location for the Mountebank executable.
    :param port: Server port.
    :param timeout: How long to wait for the Mountebank server to start.
    :param debug: Start the server in debug mode, which records all requests. This needs to be `True` for the
        :py:func:`mbtest.matchers.had_request` matcher to work.
    :param allow_injection: Allow JavaScript injection. If `True`, `local_only` should also be `True`,as per
        `Mountebank security <http://www.mbtest.org/docs/security>`_.
    :param local_only: Accept request only from localhost.
    :param data_dir: Persist all operations to disk, in this directory.
    """

    running = set()  # type: Set[int]
    start_lock = Lock()

    def __init__(
        self,
        executable: Union[str, Path] = DEFAULT_MB_EXECUTABLE,
        port: int = 2525,
        timeout: int = 5,
        debug: bool = True,
        allow_injection: bool = True,
        local_only: bool = True,
        data_dir: Union[str, None] = ".mbdb",
    ) -> None:
        super(ExecutingMountebankServer, self).__init__(port)
        with self.start_lock:
            if self.server_port in self.running:
                raise MountebankPortInUseException(
                    "Already running on port {0}.".format(self.server_port)
                )
            try:
                options = self._build_options(port, debug, allow_injection, local_only, data_dir)
                self.mb_process = subprocess.Popen([executable] + options)  # nosec
                self._await_start(timeout)
                self.running.add(port)
                logger.info(
                    "Spawned mb process %s on port %s.", self.mb_process.pid, self.server_port
                )
            except OSError:
                logger.error(
                    "Failed to spawn mb process with executable at %s. Have you installed Mountebank?",
                    executable,
                )
                raise

    @staticmethod
    def _build_options(
        port: int, debug: bool, allow_injection: bool, local_only: bool, data_dir: Union[str, None]
    ):
        options = [
            "start",
            "--port",
            str(port),
        ]  # type: List[str]
        if debug:
            options.append("--debug")
        if allow_injection:
            options.append("--allowInjection")
        if local_only:
            options.append("--localOnly")
        if data_dir:
            options += [
                "--datadir",
                data_dir,
            ]
        return options

    def _await_start(self, timeout: int) -> None:
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
            raise MountebankTimeoutError(
                "Mountebank failed to start within {0} seconds.".format(timeout)
            )

        logger.debug("Server started at %s.", self.server_url)

    def close(self) -> None:
        self.mb_process.terminate()
        self.mb_process.wait()
        self.running.remove(self.server_port)
        logger.info(
            "Terminated mb process %s on port %s status %s.",
            self.mb_process.pid,
            self.server_port,
            self.mb_process.returncode,
        )


class MountebankException(Exception):
    """Exception using Mountebank server."""

    pass


class MountebankPortInUseException(Exception):
    """Mountebank server failed to start - port already in use."""

    pass


class MountebankTimeoutError(MountebankException):
    """Mountebank server failed to start in time."""

    pass
