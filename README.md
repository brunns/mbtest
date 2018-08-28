# mbtest

Python wrapper & utils for the [Mountebank](http://www.mbtest.org/) over the wire test double tool.

Includes [pytest](https://pytest.org) fixture and [PyHamcrest](https://pyhamcrest.readthedocs.io) matchers.

[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![Build Status](https://travis-ci.org/brunns/mbtest.svg?branch=master)](https://travis-ci.org/brunns/mbtest)
[![PyPi Version](https://img.shields.io/pypi/v/mbtest.svg)](https://pypi.org/project/mbtest/releases/)
[![Licence](https://img.shields.io/github/license/brunns/mbtest.svg)](https://pypi.org/project/mbtest/)
[![Wheel](https://img.shields.io/pypi/wheel/mbtest.svg)](https://pypi.org/project/mbtest/)
[![Python Versions](https://img.shields.io/pypi/pyversions/mbtest.svg)](https://pypi.org/project/mbtest/)
[![Github all releases](https://img.shields.io/github/downloads/brunns/mbtest/total.svg)](https://GitHub.com/brunns/mbtest/releases/)
[![GitHub forks](https://img.shields.io/github/forks/brunns/mbtest.svg?style=social&label=Fork&maxAge=2592000)](https://GitHub.com/brunns/mbtest/network/)
[![GitHub stars](https://img.shields.io/github/stars/brunns/mbtest.svg?style=social&label=Star&maxAge=2592000)](https://GitHub.com/brunns/mbtest/stargazers/)
[![GitHub watchers](https://img.shields.io/github/watchers/brunns/mbtest.svg?style=social&label=Watch&maxAge=2592000)](https://GitHub.com/brunns/mbtest/watchers/)
[![GitHub contributors](https://img.shields.io/github/contributors/brunns/mbtest.svg)](https://GitHub.com/brunns/mbtest/graphs/contributors/)
[![GitHub issues](https://img.shields.io/github/issues/brunns/mbtest.svg)](https://GitHub.com/brunns/mbtest/issues/)
[![GitHub issues-closed](https://img.shields.io/github/issues-closed/brunns/mbtest.svg)](https://GitHub.com/brunns/mbtest/issues?q=is%3Aissue+is%3Aclosed)
[![GitHub pull-requests](https://img.shields.io/github/issues-pr/brunns/mbtest.svg)](https://GitHub.com/brunns/mbtest/pull/)
[![GitHub pull-requests closed](https://img.shields.io/github/issues-pr-closed/brunns/mbtest.svg)](https://GitHub.com/brunns/mbtest/pull/)

## Setup

Install with pip:

    pip install mbtest

(As usual, use of a [venv](https://docs.python.org/3/library/venv.html) or [virtualenv](https://virtualenv.pypa.io) is recommended.) Also requires [Mountebank](http://www.mbtest.org/) to have been installed:

    npm install mountebank@1.14.1 --production

## Basic example

```python
import pytest
import requests
from hamcrest import assert_that, is_
from brunns.matchers.response import response_with
from mbtest.matchers import had_request
from mbtest.imposters import Imposter, Predicate, Response, Stub

@pytest.mark.usefixtures("mock_server")
def test_request_to_mock_server(mock_server):
    # Set up mock server with required behavior
    imposter = Imposter(Stub(Predicate(path="/test"), 
                             Response(body="sausages")), 
                        record_requests=True)

    with mock_server(imposter) as server:
        # Make request to mock server
        response = requests.get("{}/test".format(imposter.url))

        assert_that("We got the expected response", 
                    response, is_(response_with(status_code=200, body="sausages")))
        assert_that("The mock server recorded the request", 
                    server, had_request(path="/test", method="GET"))
```

Needs a [pytest fixture](https://docs.pytest.org/en/latest/fixture.html), most easily defined in [`conftest.py`](https://docs.pytest.org/en/latest/fixture.html#conftest-py-sharing-fixture-functions):

```python
import pytest
from mbtest import server

@pytest.fixture(scope="session")
def mock_server(request):
    return server.mock_server(request)
```

Examples of more complex predicates can be found in the [integration tests](https://github.com/brunns/mbtest/tree/master/tests/integration/).

## Developing

Requires [tox](https://tox.readthedocs.io). Run `make precommit` tells you if you're OK to commit. For more options, run:

    make help

## Releasing

Requires [hub](https://hub.github.com/), [setuptools](https://setuptools.readthedocs.io) and [twine](https://twine.readthedocs.io). To release `n.n.n`:

    version="n.n.n" # Needs to match new version number in setup.py.
    git commit -am"Release $version" && git push # If not already all pushed, which it should be.
    hub release create $version -m"Release $version"
    python setup.py sdist
    twine upload dist/`ls -t dist/ | head -n1`
