Welcome to mbtest's documentation!
======================================

Opinionated Python wrapper & utils for the `Mountebank`_ over the wire
test double tool.

Includes `pytest`_ fixture and `PyHamcrest`_ matchers.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

      API <api.rst>

Installation
------------

Install from `Pypi <https://pypi.org/project/mbtest/>`_ as usual, using pip , `tox`_, or ``setup.py``.


Usage
-----

A basic example

.. code:: python

   import requests
   from hamcrest import assert_that, is_
   from brunns.matchers.response import response_with
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
                       response, is_(response_with(status_code=200, body="sausages")))
           assert_that("The mock server recorded the request",
                       server, had_request(path="/test", method="GET"))

Needs a `pytest fixture`_, most easily defined in `conftest.py`_:

.. code:: python

   import pytest
   from mbtest import server

   @pytest.fixture(scope="session")
   def mock_server(request):
       return server.mock_server(request)


.. _Mountebank: http://www.mbtest.org/
.. _pytest: https://pytest.org
.. _PyHamcrest: https://pyhamcrest.readthedocs.io
.. _tox: https://tox.readthedocs.io
.. _pytest fixture: https://docs.pytest.org/en/latest/fixture.html
.. _conftest.py: https://docs.pytest.org/en/latest/fixture.html#conftest-py-sharing-fixture-functions

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
