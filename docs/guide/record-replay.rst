Record and Replay
-----------------

Mountebank supports recording real upstream responses and replaying them in
subsequent test runs — useful for capturing expensive, slow, or
non-deterministic third-party API responses without hitting the real service
every time.

Recording
~~~~~~~~~

Define an imposter with a :class:`~mbtest.imposters.Proxy` response pointing at
the upstream service, then call
:meth:`~mbtest.server.MountebankServer.get_replayable_imposter` to capture the
recorded responses as concrete stubs:

.. code:: python

    import httpx
    from mbtest.imposters import Imposter, Proxy, Stub

    proxy_imposter = Imposter(Stub(responses=Proxy(to="http://example.com", mode=Proxy.Mode.ONCE)))

    with mock_server(proxy_imposter) as server:
        # Make the requests you want to record
        httpx.get(str(proxy_imposter.url / "api/data"))

        # Retrieve a replayable imposter with proxy responses captured as stubs
        replayable = server.get_replayable_imposter(proxy_imposter)

Saving and loading
~~~~~~~~~~~~~~~~~~

Persist the replayable imposter to a JSON file:

.. code:: python

    replayable.save("recorded_responses.json")

In future test runs, load the file instead of proxying the upstream service:

.. code:: python

    from mbtest.imposters import Imposter

    imposter = Imposter.from_file("recorded_responses.json")

    with mock_server(imposter):
        # Tests run against recorded responses, no upstream service needed
        response = httpx.get(str(imposter.url / "api/data"))
