# encoding=utf-8
import logging
import subprocess  # nosec
import time
from collections import abc
from operator import attrgetter
from pathlib import Path
from threading import Lock
from typing import Iterable, List, MutableSequence, Optional, Sequence, Set, Union

import requests
from _pytest.fixtures import FixtureRequest  # type: ignore
from furl import furl
from requests import RequestException

from mbtest.imposters import Imposter
from mbtest.imposters.imposters import Request
from mbtest.util import find_mountebank_executable

logger = logging.getLogger(__name__)

DEFAULT_MB_EXECUTABLE = find_mountebank_executable()


def mock_server(
    request: FixtureRequest,
    executable: Union[str, Path] = DEFAULT_MB_EXECUTABLE,
    port: int = 2525,
    timeout: int = 5,
    debug: bool = True,
    allow_injection: bool = True,
    local_only: bool = True,
    data_dir: Union[str, None] = ".mbdb",
) -> "MountebankServer":
    """`Pytest fixture <https://docs.pytest.org/en/latest/fixture.html>`_, making available a mock server, running one
    or more imposters, one for each domain being mocked.

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
                r = requests.get(f"{imposter.url}/test")

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

            with mb(imposter):
                r = requests.get(f"{imposter.url}/test")

                assert_that(r, is_response().with_status_code(200).and_body("sausages"))
                assert_that(imposter, had_request(path='/test', method="GET"))

    Imposters will be torn down when the `with` block is exited.

    :param port: Server port.
    :param scheme: Server scheme, if not `http`.
    :param host: Server host, if not `localhost`.
    :param imposters_path: Imposters path, if not `imposters`.

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
        self._running_imposters: MutableSequence[Imposter] = []

    def __call__(self, imposters: Sequence[Imposter]) -> "MountebankServer":
        self.imposters = imposters
        return self

    def __enter__(self) -> "MountebankServer":
        self.add_imposters(self.imposters)
        return self

    def __exit__(self, ex_type, ex_value, ex_traceback) -> None:
        self.delete_imposters()

    def add_imposters(self, definition: Union[Imposter, Iterable[Imposter]]) -> None:
        """Add imposters to Mountebank server.

        :param definition: One or more Imposters.
        """
        if isinstance(definition, abc.Iterable):
            for imposter in definition:
                self.add_imposters(imposter)
        else:
            self.add_impostor(definition)

    def add_impostor(self, definition):
        """Add single imposter to Mountebank server.

        :param definition: One or more Imposters."""
        json = definition.as_structure()
        post = requests.post(self.server_url, json=json, timeout=10)
        post.raise_for_status()
        definition.attach(self.host, post.json()["port"], self.server_url)
        self._running_imposters.append(definition)

    def delete_imposters(self) -> None:
        """Delete all impostors from server."""
        while self._running_imposters:
            self.delete_impostor(self._running_imposters[0])

    def delete_impostor(self, imposter):
        """Delete impostor from server."""
        requests.delete(imposter.configuration_url, timeout=30).raise_for_status()
        self._running_imposters = [
            i for i in self._running_imposters if i.configuration_url != imposter.configuration_url
        ]

    def get_actual_requests(self) -> Sequence[Request]:
        actual_requests: MutableSequence[Request] = []
        for imposter in self._running_imposters:
            actual_requests += imposter.get_actual_requests()
        return actual_requests

    @property
    def server_url(self) -> furl:
        return furl().set(
            scheme=self.scheme, host=self.host, port=self.server_port, path=self.imposters_path
        )

    def query_all_imposters(self) -> Sequence[Imposter]:
        """Yield all imposters running on the server, including those defined elsewhere."""
        server_info = requests.get(self.server_url, timeout=30)
        imposters_structure = server_info.json()["imposters"]
        all_imposters: MutableSequence[Imposter] = []
        for imposter_structure in imposters_structure:
            impostor_url = imposter_structure["_links"]["self"]["href"]
            imposter = Imposter.from_structure(requests.get(impostor_url, timeout=30).json())
            imposter.host = self.host
            imposter.server_url = self.server_url
            all_imposters.append(imposter)
        return sorted(all_imposters, key=attrgetter("port"))

    def import_running_imposters(self) -> None:
        """Replaces all running imposters with those defined on the server"""
        self._running_imposters = []
        for imposter in self.query_all_imposters():
            self._running_imposters.append(imposter)

    def get_running_imposters(self) -> Sequence[Imposter]:
        """Returns all imposters that the instance is aware of"""
        return self._running_imposters


class ExecutingMountebankServer(MountebankServer):
    """A Mountebank mock server, running one or more imposters, one for each domain being mocked.

    Test will look like::

        def test_an_imposter(mock_server):
            mb = ExecutingMountebankServer()
            imposter = Imposter(Stub(Predicate(path='/test'),
                                     Response(body='sausages')),
                                record_requests=True)

            with mb(imposter) as s:
                r = requests.get(f"{imposter.url}/test")

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

    running: Set[int] = set()
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
        super().__init__(port)
        with self.start_lock:
            if self.server_port in self.running:
                raise MountebankPortInUseException(f"Already running on port {self.server_port}.")
            try:
                options = self._build_options(port, debug, allow_injection, local_only, data_dir)
                self.mb_process = subprocess.Popen([str(executable)] + options)  # nosec
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
        port: int, debug: bool, allow_injection: bool, local_only: bool, data_dir: Optional[str]
    ) -> List[str]:
        options: List[str] = ["start", "--port", str(port)]
        if debug:
            options.append("--debug")
        if allow_injection:
            options.append("--allowInjection")
        if local_only:
            options.append("--localOnly")
        if data_dir:
            options += ["--datadir", data_dir]
        return options

    def _await_start(self, timeout: int) -> None:
        start_time = time.time()
        started = False

        while time.time() - start_time < timeout:
            try:
                requests.get(self.server_url, timeout=1).raise_for_status()
                started = True
                break
            except RequestException:
                started = False
                time.sleep(0.1)

        if not started:
            raise MountebankTimeoutError(f"Mountebank failed to start within {timeout} seconds.")

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


class MountebankPortInUseException(Exception):
    """Mountebank server failed to start - port already in use."""


class MountebankTimeoutError(MountebankException):
    """Mountebank server failed to start in time."""
