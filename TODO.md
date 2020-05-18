# To Do

* What if Mountebank is installed elsewhere? We should emit better messages if starting the mb server fails, and make the location configurable. This could be as simple as parameterising it. 
* Does the TCP protocol stuff work? I need to add `endOfRequestResolver` I think, at least.
* `NotPredicate`
* Proxy record/playback
* Test for saving & rehydrating impostors from file.
* Tutorial
    * Basics
    * Stubs, predicates, responses
    * Stubbing vs. Mocking
    * Server options
        * Existing server
    * Proxies
        * Record/Playback
* Fix email matcher
* `had_request()` matcher for impostors - deprecate server version?
