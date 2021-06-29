# Change Log

## 2.9.0

* Enhancement #57, changes to allow modification of stubs and impostors on an already running Mountebank server. (Thanks [@jbackman](https://github.com/jbackman).)
* Enhancement #56, improve finding of `DEFAULT_MB_EXECUTABLE`. (Thanks [@jbackman](https://github.com/jbackman).)
* Fix #57, exception Stub.from_structure() for stubs with inject response.

## 2.8.1

* Fix #52, exception building HttpResponse from structure with no mode specified. (Thanks [@jbackman](https://github.com/jbackman).)

## 2.8

* Add default_response attribute to Impostor.

## 2.7

* HTTPS support.

## 2.6.1

* Bugfix - Stub.from_structure() decodes logically combinable predicates. (Thanks, [@SShatun](https://github.com/SShatun).)

## 2.6

* Add support for PATCH HTTP verb. (Thanks to [@garry-jeromson](https://github.com/garry-jeromson).)
* Add NotPredicate.

## 2.5.1

* Bugfix - Ensure imposter host matches server host

## 2.5

* Add [dynamic predicates and responses](http://www.mbtest.org/docs/api/injection). This feature requires Mountebank 2.0 or later, but all other features should continue to work with older version.
* Add MountebankServer.query_all_imposters() method to retrieve all imposters from a running MB server, including those not created locally.

## 2.4 

* Allow MountebankServer to attach to an already running MB instance on another host.
* Make has_request() a builder style matcher, and use builder matcher construction wherever possible.

## 2.3

* Allow MountebankServer to attach to an already running MB instance. Split out execute-server behavior from MountebankServer class into new ExecutingMountebankServer.
* Python 3.8 supported.
