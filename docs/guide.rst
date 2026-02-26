Guide
=====

``mbtest`` provides a Pythonic wrapper around `Mountebank`_, an over-the-wire test double tool.
This guide covers the main concepts and common usage patterns.

.. toctree::
   :maxdepth: 2
   :caption: Advanced Topics:

   Use with Docker <guide/docker.rst>
   Record and Replay <guide/record-replay.rst>

Getting started
---------------

The ``mock_server`` fixture launches a Mountebank process for the test session and shuts it
down when the session ends. Add it to your ``conftest.py``:

.. code:: python

   import pytest
   from mbtest import server

   @pytest.fixture(scope="session")
   def mock_server(request):
       return server.mock_server(request)

This requires Mountebank to be installed::

    $ npm install mountebank@2.9 --omit=dev

A minimal test:

.. code:: python

   import httpx
   from hamcrest import assert_that
   from brunns.matchers.response import is_response
   from mbtest.matchers import had_request
   from mbtest.imposters import Imposter, Predicate, Response, Stub

   def test_request_to_mock_server(mock_server):
       imposter = Imposter(Stub(Predicate(path="/test"), Response(body="sausages")))

       with mock_server(imposter):
           response = httpx.get(f"{imposter.url}/test")

           assert_that(response, is_response().with_status_code(200).and_body("sausages"))
           assert_that(imposter, had_request().with_path("/test").and_method("GET"))

The ``with mock_server(imposter):`` block registers the imposter with Mountebank and tears it
down on exit. ``imposter.url`` is only available inside the block, once Mountebank has
assigned the port.

Imposters
---------

An :class:`~mbtest.imposters.Imposter` is a mock server listening on a port. The port is
allocated randomly by Mountebank if you don't specify one:

.. code:: python

   imposter = Imposter(Stub(), port=4567, name="my-service")

Multiple imposters can be started together in one ``with`` block:

.. code:: python

   with mock_server([imposter1, imposter2]):
       ...

The ``default_response`` parameter sets what Mountebank returns when no stub matches:

.. code:: python

   from mbtest.imposters.responses import HttpResponse

   imposter = Imposter(
       Stub(Predicate(path="/known"), Response(body="yes")),
       default_response=HttpResponse(body="unknown endpoint", status_code=404),
   )

Supported protocols are HTTP, HTTPS, SMTP, and TCP:

.. code:: python

   Imposter(Stub(), protocol=Imposter.Protocol.HTTPS)

Stubs
-----

A :class:`~mbtest.imposters.Stub` pairs predicates (conditions) with responses. Mountebank
evaluates stubs in order and uses the first one whose predicates match. An imposter with
multiple stubs implements a fallback chain:

.. code:: python

   imposter = Imposter(
       stubs=[
           Stub(Predicate(path="/api/orders"), Response(body="orders")),
           Stub(Predicate(path="/api/items"),  Response(body="items")),
           Stub(responses=Response(status_code=404)),  # fallback
       ]
   )

Both ``predicates`` and ``responses`` accept a single object or a list.

Predicates
----------

A :class:`~mbtest.imposters.Predicate` matches on any combination of request fields:

.. code:: python

   Predicate(
       path="/api/orders",
       method="POST",
       query={"status": "pending"},
       headers={"Content-Type": "application/json"},
       body='{"qty": 1}',
   )

The default operator is ``equals``. Other operators let you do partial and pattern matching:

.. code:: python

   Predicate(path="/api/", operator=Predicate.Operator.STARTS_WITH)
   Predicate(body="error",  operator=Predicate.Operator.CONTAINS)
   Predicate(path=r"^/v\d+/", operator=Predicate.Operator.MATCHES)

Available operators: ``EQUALS``, ``DEEP_EQUALS``, ``CONTAINS``, ``STARTS_WITH``,
``ENDS_WITH``, ``MATCHES``, ``EXISTS``.

Combining predicates
~~~~~~~~~~~~~~~~~~~~

Use ``&`` (AND), ``|`` (OR), and ``~`` (NOT) to build composite predicates:

.. code:: python

   # Both conditions must match
   predicate = Predicate(path="/test") & Predicate(method="POST")

   # Either condition matches
   either = Predicate(path="/a") | Predicate(path="/b")

   # Inverts the match
   not_admin = ~Predicate(path="/admin")

When you pass a *list* of predicates to a :class:`~mbtest.imposters.Stub`, Mountebank
treats them as an implicit AND — all predicates in the list must match. Using ``&``
produces the same effect with a single, composable predicate object.

XPath and JSONPath
~~~~~~~~~~~~~~~~~~

Predicates support XPath and JSONPath selectors for structured request bodies:

.. code:: python

   Predicate(xpath="//order/qty", body="1")
   Predicate(jsonpath="$.order.qty", body="1")

Injection
~~~~~~~~~

For advanced cases, :class:`~mbtest.imposters.predicates.InjectionPredicate` accepts a
JavaScript function string (requires ``--allowInjection`` on the Mountebank server):

.. code:: python

   from mbtest.imposters.predicates import InjectionPredicate

   InjectionPredicate(inject="(request) => request.path === '/test'")

Responses
---------

A :class:`~mbtest.imposters.Response` defines what the mock server returns:

.. code:: python

   Response(
       body="sausages",
       status_code=200,
       headers={"Content-Type": "text/plain"},
   )

The ``body`` can be a string or any JSON-serialisable data structure.

Response behaviors
~~~~~~~~~~~~~~~~~~

**Latency** — ``wait`` adds a delay in milliseconds:

.. code:: python

   Response(body="slow response", wait=500)

**Cycling** — provide a list of responses and Mountebank cycles through them in order,
one per request:

.. code:: python

   Stub(
       Predicate(path="/api"),
       [Response(body="first"), Response(body="second"), Response(body="third")],
   )

**Repeat** — repeat a response a given number of times before moving to the next:

.. code:: python

   Stub(
       Predicate(path="/api"),
       [Response(body="busy", repeat=3), Response(body="ok")],
   )

Fault simulation
~~~~~~~~~~~~~~~~

:class:`~mbtest.imposters.responses.FaultResponse` simulates network-level errors rather
than returning an HTTP response:

.. code:: python

   from mbtest.imposters.responses import FaultResponse

   Stub(responses=FaultResponse(FaultResponse.Fault.CONNECTION_RESET_BY_PEER))

Available faults: ``CONNECTION_RESET_BY_PEER``, ``RANDOM_DATA_THEN_CLOSE``.

Injection
~~~~~~~~~

:class:`~mbtest.imposters.responses.InjectionResponse` accepts a JavaScript function
string for fully dynamic responses (requires ``--allowInjection``):

.. code:: python

   from mbtest.imposters.responses import InjectionResponse

   InjectionResponse(inject="(request, state) => ({ statusCode: 200, body: request.path })")

Stubbing vs. mocking
--------------------

**Stubbing** means pre-programming the mock server with fixed responses and not asserting
on what requests it received. Use it when you only care that your code doesn't blow up.

**Mocking** means additionally asserting on the requests the mock server received. Use
:func:`~mbtest.matchers.had_request` for this.

In ``mbtest`` the distinction is just whether you call ``assert_that(imposter, had_request(...))``
— the same :class:`~mbtest.imposters.Imposter` object supports both. Request recording is
controlled by the ``record_requests`` parameter on the imposter (``True`` by default, as
long as the Mountebank server is started with ``--debug``, which the ``mock_server`` fixture
does automatically).

Assertions and matchers
-----------------------

Checking HTTP requests
~~~~~~~~~~~~~~~~~~~~~~

:func:`~mbtest.matchers.had_request` verifies that an imposter recorded a matching request.
Build the criteria using the fluent ``with_`` / ``and_`` interface:

.. code:: python

   from hamcrest import assert_that, has_entry
   from mbtest.matchers import had_request

   assert_that(imposter, had_request().with_path("/api/orders").and_method("POST"))
   assert_that(imposter, had_request().with_query({"status": "pending"}))
   assert_that(imposter, had_request().with_headers(has_entry("Authorization", "Bearer token")))

Any `PyHamcrest`_ matcher can be used in place of a literal value:

.. code:: python

   from hamcrest import contains_string

   assert_that(imposter, had_request().with_body(contains_string("qty")))

To match the parsed JSON body, use ``with_json``:

.. code:: python

   from hamcrest import has_entries

   assert_that(imposter, had_request().with_json(has_entries(qty=1)))

To check the number of times a request was received:

.. code:: python

   assert_that(imposter, had_request().with_path("/api").and_times(3))

The matcher can also be applied to the server object to check across all imposters:

.. code:: python

   with mock_server([imposter1, imposter2]) as server:
       ...
       assert_that(server, had_request().with_method("GET"))

SMTP
----

Use the :func:`~mbtest.imposters.smtp_imposter` factory to create an SMTP imposter (defaults
to port 5525), then assert on emails received using :func:`~mbtest.matchers.email_sent`:

.. code:: python

   import smtplib
   from hamcrest import assert_that
   from mbtest.imposters import smtp_imposter
   from mbtest.matchers import email_sent

   def test_sends_email(mock_server):
       imposter = smtp_imposter()

       with mock_server(imposter):
           smtp = smtplib.SMTP()
           smtp.connect(host=imposter.host, port=imposter.port)
           smtp.sendmail(from_addr, [to_addr], message_string)
           smtp.quit()

           assert_that(imposter, email_sent(subject="Order confirmation", body_text="Thank you"))

.. _Mountebank: https://github.com/bbyars/mountebank
.. _PyHamcrest: https://pyhamcrest.readthedocs.io
