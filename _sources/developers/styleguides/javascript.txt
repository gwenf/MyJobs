===========================
JavaScript Coding Standard
===========================

Goals
=====

Our deliverable is a set of app specific JS bundles, and a ``vendor.js`` bundle
which contains code shared by all apps.

* Minimize development build time and size of our app specific JS bundles.
* We should thoroughly discuss any changes that might increase the size of our
  deliverable ``vendor.js`` size, especially when alternatives exist
* Although we tolerate a longer build and larger delivered size of our
  ``vendor.js`` bundle, it should at least not contain dead code.
* As JS tools evolve and mature, we want to gain leverage from these
  improvements.

  * Minimize instances of "oops, we can't upgrade because..."

Style
=====

* We follow the [AirBnB](https://github.com/airbnb/javascript) standard.
* Document any exceptions here.
* Developers should run the lint tool and keep the report clean. Any mistakes
  should be fixed as part of the PR process.

Code Locations
==============

New JS code goes under the "gulp" folder, which contains our JS application
code and the infrastructure for building it into app appropriate bundles.

Subfolders
----------

* ``common``: modules that might be used in multiple apps.
* ``reporting``, ``nonuseroutreach`` etc.: app specific folders.
* each app folder should contain a main.js file.

  * This is the starting point for bootstrapping the application.
  * It will generally contain some object instantiation and React ``render``
    calls.
  * It should be short.

* the app folders should contain separate modules for business logic and app
  specific components. 
* the app folders should contain a spec folder which itself contains Jasmine
  tests.

Desired Design Practices
------------------------

We expect exceptions to these practices.

* Interactive views should be rendered in React components.

  * Break components down to small composable pieces.
  * Limit functionality. Avoid "business logic."

    * Accept props.
    * Respond to events.
    * Set internal state.
    * Invoke callbacks, via props.

  * If interacting with business logic object instances, don't pass those down
    to child components. Pass down callbacks only.

* Business logic should be written using modern idiomatic JS functions and
  classes.

  * Choose promises over callbacks when possible.
  * Use async/await when responding to promises.
  * Use separate classes for processing data and interacting with external
    services (API).

    * For a smaller app, having a class dedicated to calling the API and
      returning the result in a promise is often sufficient.
    * Use dependency injection techniques to keep unit test coverage of
      important classes high.

  * Don't enforce critical invariants (security, etc.) in the client code at
    all. That should be done in the backend API.

* Unit tests of business logic should not require a lot of extra libraries.

  * Instantiate classes, invoke functions, check results, state, etc.
  * Tests should not call external API's or do significant IO.
  * Business logic tests should not mess with React, the DOM, etc.

* Future: Unit tests of view code should also be fast and IO free.

  * Set up props.
  * Simulate events.
  * Verify state.
  * Should not require real DOM.

Library Policy
==============

* Implement as much of our business logic as possible in idiomatic JS. (i.e.,
  not React)

  * Future: Keep the libraries we use up to date. (?? when, exactly ??)
  * Gain as much leverage as possible from as few libraries as possible.

    * React
    * Jasmine
    * Polyfills

* Scrutinize new library additions carefully.

  * Are there hidden licensing issues?
  * Will this further bloat our bundles or startup time?
  * Could the total cost of implementing this library be surprisingly bad in
    the future?
  * Would a trivial self written function or component be sufficient?
  * Is this library going to entangle our business logic in a way that will
    harm upgrades?
  * When this library dies someday, will that harm us?
  * Will use of this library prevent us from upgrading other libraries in the
    future? (i.e. some prebuilt react component, only works with React 0.13.
    Oops.)
  * Are we bringing in a large library only to use a very small part of it?
    (using a tank where a stick would do)

* Avoid editing ``package.json`` by hand. Use ``npm install --save`` and
  other npm commands as much as possible. These automatically keep the
  shrinkwrap file up to date.

* NPM likes to put a lot of unstable information in the shrinkwrap file.
  If you find a lot of extraneous lines in the diff of ``npm-shrinkwrap.json``,
  run ``npm run clean-shrinkwrap``. The diff should be much cleaner and give
  some insight into the consequenes of the library change.

Practices
=========

* Write unit tests for new code.
* Keep unit tests passing.
* Keep unit tests fast.
* Keep lint report clean.

React Conventions
=================

* There should be one React component per file. Use ``export default`` to
  export it.

  * Document the react component with a ``/**`` comment at the top of the
    component class or function.
  * Keep propTypes up to date. Document what each prop means.

* Write controlled components.
* Keep separation between components which define a lot of user interaction and
  components which compose other components to build a user application.

Redux Conventions
=================

* The most important documentation is the documentation of the reducer
  functions. Put a `/**` comment at the top of the reducer function.

  * Make clear the concept behind each prop.
  * Don't describe what the UI does, at that is likely to change.
  * Bad example: "active: make item blue"
  * Good example:

::

    /**
     *  format for user list {
     *
     *    users: [
     *      id: integer, database id for this user
     *      name: string, display name for this user
     *      active: boolean indicating that the user working on this item.
     *    ]
     *  }
     */
    export default handleActions({

* Also document compound actions with ``/**`` comments

  * Describe the action in terms of why it is occuring.
  * Include descriptions 
  * Example:

::

    /**
     * The user is done working and ready to see the result
     *
     * dryRun: don't save the result, just show a preview
     */
    export function submitWork(dryRun) {

* Encode as much business logic as possible into redux reducers.
* Keep business logic out of React components. It is necessary to do the
  occasional dom tweak or auto-scroll in React, but this should not be common.
* Write action creators to conform to "Standard Flux Actions".
* When unit testing reducers, just invoke them as functions and check their
  result.
* When unit testing compound actions, you can either invoke them as functions
  or create a redux store and dispatch them.
