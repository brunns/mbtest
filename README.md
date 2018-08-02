# mbtest

Python wrapper & utils for the [Mountebank](http://www.mbtest.org/) over the wire test double tool.

Includes [pytest](https://pytest.org) fixture and [PyHamcrest](https://pyhamcrest.readthedocs.io) matchers.

[![Build Status](https://travis-ci.org/brunns/mbtest.svg?branch=master)](https://travis-ci.org/brunns/mbtest)

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

Examples of more complex predicates can be found in the [integration tests](tests/integration/).

## Developing

Requires [tox](https://tox.readthedocs.io). Run `make precommit` tells you if you're OK to commit. For more options, run:

    make help

## Releasing

Requires [hub](https://hub.github.com/), [setuptools](https://setuptools.readthedocs.io) and [twine](https://twine.readthedocs.io). To release `n.n.n`:

    git commit -am"Release n.n.n" && git push # If not already all pushed, which it should be.
    hub release create n.n.n -m"Release n.n.n"
    python setup.py sdist
    twine upload dist/`ls -t dist/ | head -n1`
