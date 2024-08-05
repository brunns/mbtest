# mbtest

Opinionated Python wrapper & utils for the [Mountebank](https://www.mbtest.org/) over the wire test double tool.

Includes [pytest](https://pytest.org) fixture and [PyHamcrest](https://pyhamcrest.readthedocs.io) matchers.

[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![Continuous Integration](https://github.com/brunns/mbtest/workflows/Continuous%20Integration/badge.svg)](https://github.com/brunns/mbtest/actions)
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

    npm install mountebank@2.9 --omit=dev

(Alternatively, you can attach to an instance of Mountebank running elsewhere, perhaps [in docker](https://mbtest.readthedocs.io/en/latest/guide/docker.html).)

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

    with mock_server(imposter):
        # Make request to mock server - exercise code under test here
        response = requests.get(f"{imposter.url}/test")

        assert_that("We got the expected response", 
                    response, is_response().with_status_code(200).and_body("sausages"))
        assert_that("The mock server recorded the request", 
                    imposter, had_request().with_path("/test").and_method("GET"))
```

Needs a [pytest fixture](https://docs.pytest.org/en/latest/fixture.html), most easily defined in [`conftest.py`](https://docs.pytest.org/en/latest/how-to/fixtures.html#scope-sharing-fixtures-across-classes-modules-packages-or-session):

```python
import pytest
from mbtest import server

@pytest.fixture(scope="session")
def mock_server(request):
    return server.mock_server(request)
```

This will take care of starting and stopping the Mountebank server for you. Examples of more complex predicates can be 
found in the [integration tests](https://github.com/brunns/mbtest/tree/master/tests/integration/).

See the [Documentation](https://mbtest.readthedocs.io/) for more.


## Contributing

Requires [make](https://www.gnu.org/software/make/manual/html_node/index.html) and [tox](https://tox.readthedocs.io). 
[PyEnv](https://github.com/pyenv/pyenv) may also come in handy so tests can be run against various Python versions. 

Integration tests run against an instance of Mountebank running in Docker.

Currently, the `Makefile` targets use Python 3.8 and 3.11 via tox, so a quick-start setup could be:

```sh
brew install pyenv colima docker
versions=(3.8 3.12)
for v in "${versions[@]}"; do pyenv install $v -s; done
pyenv local 3.8 3.12
pip install tox tox-pyenv
colima start
```

In order to run `make test`, you'll also need to have Mountebank installed locally:

```sh
npm install mountebank@2.9 --production
```

(`mbtest` is tested against Mountebank versions back as far as 1.16, but obviously only features supported by the Mountebank version you're using will work.)

After that, you should be ready to roll; running `make test` will let you know if your setup is correct.

Running `make precommit` tells you if you're OK to commit. For more options, run:

    make help

## Releasing

Requires [gh](https://cli.github.com/), [setuptools](https://setuptools.readthedocs.io),
[wheel](https://github.com/pypa/wheel) and [twine](https://twine.readthedocs.io). To release version `n.n.n`, first
update the version number in `setup.py`, then:

```sh
version="n.n.n" # Needs to match new version number in setup.py.
git checkout -b "release-$version"
make precommit && git commit -am"Release $version" && git push --set-upstream origin "release-$version" # If not already all pushed, which it should be.
gh release create "V$version" --target "release-$version" --generate-notes
python setup.py sdist bdist_wheel && twine upload dist/*$version*
git checkout master && git merge "release-$version"
git push
```
