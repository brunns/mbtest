# To Do

* [`HTTPS`](http://www.mbtest.org/docs/protocols/https) test - might not work yet! Try [trustme](https://github.com/python-trio/trustme) for the certs.
* What if Mountebank is installed elsewhere? We should emit better messages if starting the mb server fails.
* Does the [TCP](http://www.mbtest.org/docs/protocols/tcp) protocol stuff work? I need to add `endOfRequestResolver` I think, at least.
* Proxy record/playback
* Tutorial & guide
* `had_request()` matcher for imposters - deprecate server version?
* CONTRIBUTING.md

## CI
* Publish coverage
* Release process