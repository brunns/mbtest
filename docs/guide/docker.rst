Use with Docker
---------------

If you want to use your own mountebank service instance (`Docker`_, for
example) you have **no need to use npm** requirements.

.. code:: sh

   docker run -p 2525:2525 -p IMPOSTER_PORT:IMPOSTER_PORT -d andyrbell/mountebank

You can do like this in your [``conftest.py``]:

.. code:: python

   import pytest
   from mbtest.server import MountebankServer

   @pytest.fixture(scope="session")
   def mock_server():
       return MountebankServer(port=2525, host="localhost")

Don’t forget to open docker ports for mountebank (default 2525) and for
each it’s imposters.

.. code:: python

   from mbtest.imposters import Imposter, Predicate, Response, Stub

   imposter = Imposter(
       Stub(
           Predicate(path="/test") & Predicate(query={}) & Predicate(method="GET"),
           Response(body="sausages")
       ),
       record_requests=True,
       port=IMPOSTER_PORT)

   with mock_server(imposter) as ms:
       response = requests.get("{}/test".format(imposter.url))
       # Check your request
       print(ms.get_actual_requests())

If you don’t specify port for Imposter it will be done randomly.

Extra
-----

You can combine your Predicate with ``&``\ (and), ``|``\ (or).

.. _Docker: https://hub.docker.com/r/andyrbell/mountebank