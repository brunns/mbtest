# mbtest

Opinionated Python wrapper & utils for the [Mountebank](http://www.mbtest.org/) over the wire test double tool.

Includes [pytest](https://pytest.org) fixture and [PyHamcrest](https://pyhamcrest.readthedocs.io) matchers.

[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![Build Status](https://travis-ci.org/brunns/mbtest.svg?branch=master&logo=travis)](https://travis-ci.org/brunns/mbtest)
[![PyPi Version](https://img.shields.io/pypi/v/mbtest.svg?logo=pypi)](https://pypi.org/project/mbtest/#history)
[![Python Versions](https://img.shields.io/pypi/pyversions/mbtest.svg?logo=python)](https://pypi.org/project/mbtest/)
[![Licence](https://img.shields.io/github/license/brunns/mbtest.svg)](https://github.com/brunns/mbtest/blob/master/LICENSE)
[![GitHub all releases](https://img.shields.io/github/downloads/brunns/mbtest/total.svg?logo=github)](https://github.com/brunns/mbtest/releases/)
[![GitHub forks](https://img.shields.io/github/forks/brunns/mbtest.svg?label=Fork&logo=github)](https://github.com/brunns/mbtest/network/members)
[![GitHub stars](https://img.shields.io/github/stars/brunns/mbtest.svg?label=Star&logo=github)](https://github.com/brunns/mbtest/stargazers/)
[![GitHub watchers](https://img.shields.io/github/watchers/brunns/mbtest.svg?label=Watch&logo=github)](https://github.com/brunns/mbtest/watchers/)
[![GitHub contributors](https://img.shields.io/github/contributors/brunns/mbtest.svg?logo=github)](https://github.com/brunns/mbtest/graphs/contributors/)
[![GitHub issues](https://img.shields.io/github/issues/brunns/mbtest.svg?logo=github)](https://github.com/brunns/mbtest/issues/)
[![GitHub issues-closed](https://img.shields.io/github/issues-closed/brunns/mbtest.svg?logo=github)](https://github.com/brunns/mbtest/issues?q=is%3Aissue+is%3Aclosed)
[![GitHub pull-requests](https://img.shields.io/github/issues-pr/brunns/mbtest.svg?logo=github)](https://github.com/brunns/mbtest/pulls)
[![GitHub pull-requests closed](https://img.shields.io/github/issues-pr-closed/brunns/mbtest.svg?logo=github)](https://github.com/brunns/mbtest/pulls?utf8=%E2%9C%93&q=is%3Apr+is%3Aclosed)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/3b7c694664974d17a34e594c43af0c1b)](https://www.codacy.com/app/brunns/mbtest)
[![Codacy Coverage](https://api.codacy.com/project/badge/coverage/3b7c694664974d17a34e594c43af0c1b)](https://www.codacy.com/app/brunns/mbtest)
[![Documentation Status](https://readthedocs.org/projects/mbtest/badge/?version=latest)](https://mbtest.readthedocs.io/en/latest/?badge=latest)
[![Lines of Code](https://tokei.rs/b1/github/brunns/mbtest)](https://github.com/brunns/mbtest)

## Setup

Install with pip:

    pip install mbtest

(As usual, use of a [venv](https://docs.python.org/3/library/venv.html) or [virtualenv](https://virtualenv.pypa.io) is recommended.) Also requires [Mountebank](http://www.mbtest.org/) to have been installed:

    npm install mountebank@2.2 --production

## Basic example

```python
import requests
from hamcrest import assert_that
from brunns.matchers.response import is_response
from mbtest.matchers import had_request
from mbtest.imposters import Imposter, Predicate, Response, Stub

def test_request_to_mock_server(mock_server):
    # Set up mock server with required behavior
    imposter = Imposter(Stub(Predicate(path="/test"), 
                             Response(body="sausages")))

    with mock_server(imposter) as server:
        # Make request to mock server - exercise code under test here
        response = requests.get("{}/test".format(imposter.url))

        assert_that("We got the expected response", 
                    response, is_response().with_status_code(200).and_body("sausages"))
        assert_that("The mock server recorded the request", 
                    server, had_request().with_path("/test").and_method("GET"))
```

Needs a [pytest fixture](https://docs.pytest.org/en/latest/fixture.html), most easily defined in [`conftest.py`](https://docs.pytest.org/en/latest/fixture.html#conftest-py-sharing-fixture-functions):

```python
import pytest
from mbtest import server

@pytest.fixture(scope="session")
def mock_server(request):
    return server.mock_server(request)
```

This will take care of starting and stopping the Mountebank server for you. Examples of more complex predicates can be found in the [integration tests](https://github.com/brunns/mbtest/tree/master/tests/integration/).

## Developing

Requires [make](https://www.gnu.org/software/make/manual/html_node/index.html) and [tox](https://tox.readthedocs.io). [PyEnv](https://github.com/pyenv/pyenv) may also come in handy so tests can be run against various Python versions.  Run `make precommit` tells you if you're OK to commit. For more options, run:

    make help

## Releasing

Requires [hub](https://hub.github.com/), [setuptools](https://setuptools.readthedocs.io) and [twine](https://twine.readthedocs.io). To release version `n.n.n`:

    version="n.n.n" # Needs to match new version number in setup.py.
    git checkout -b "release-$version"
    make precommit && git commit -am"Release $version" && git push # If not already all pushed, which it should be.
    hub release create "V$version" -t"release-$version" -m"Version $version"
    python setup.py sdist bdist_wheel
    twine upload dist/*$version*
