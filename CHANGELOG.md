# Change Log

## 2.5

* Add [dynamic predicates and responses](http://www.mbtest.org/docs/api/injection). This feature requires Mountebank 2.0 or later, but all other features should continue to work with older version.
* Add MountebankServer.query_all_imposters() method to retrieve all imposters from a running MB server, including those not created locally.

## 2.4 

* Allow MountebankServer to attach to an already running MB instance on another host.
* Make has_request() a builder style matcher, and use builder matcher construction wherever possible.

## 2.3

* Allow MountebankServer to attach to an already running MB instance. Split out execute-server behavior from MountebankServer class into new ExecutingMountebankServer.
* Python 3.8 supported.
