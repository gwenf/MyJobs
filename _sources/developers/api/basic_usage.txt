=======================
My.jobs API Basic Usage
=======================

Updated Dec 4, 2013

About the API
=============

The My.jobs api provides access to common data and functions on the My.jobs platform via a url-based REST model. It is built on TastyPie and Django, and returns data in either JSON or JSONp formats.

Saved Search API
================

In order to create a saved search via the API, you must make two calls. First to the user api to check if the email is already in the system, and the second call to create the saved search itself.

**Usage**

Step 1: Call the user API to see if the email submitted already exists

.. list-table::
    :header-rows: 0
    :stub-columns: 1

    * - Example
      - https://secure.my.jobs/api/v1/user/?email=pat@email.com&username=you@yourcompany.com&api_key=1234567890abcdefghijklmnop
    * - URL
      - https://secure.my.jobs/api/v1/user/
    * - Required Parameters
      - **email**

        The email to check for account status. If the email is not associated with an account, an account will be created for them and a verification email will be sent to the user.

        **username**

        The API username is unique to your organization.

        **api_key**

        The API key associated with the above username
    * - Optional Parameters
      - **callback**

        If this parameter is provided, then the response will be returned as JSONp instead of JSON.
    * - Response Format
      - **JSON**

        {"email": "[provided email]", "user_created": [true|false]}

        **JSONp**

        callback({"email": "[provided email]", "user_created": [true|false]})
    * - Response Values
      - **email**

        The email address of the new account. This should always match the email passed to the api. If there is an error, the email field will contain the error message.

        **user_created**

        Returns true if the user was created, false if the user already exists.

Step 2: Call the saved search API to create the saved search

.. list-table::
    :header-rows: 0
    :stub-columns: 1

    * - Example
      - https://secure.my.jobs/api/v1/savedsearch/?callback=finish_ss&email=pat@email.com&url=http%3A%2F%2Fwww.my.jobs%2Fjobs%2F%3Fq%3Dinternet&username=you@yourcompany.com&api_key=1234567890abcdefghijklmnop
    * - URL
      - https://secure.my.jobs/api/v1/savedsearch/
    * - Required Parameters
      - **email**

        The email of the account that will own the saved search. If the email is not associated with an account, the api will return an error.

        **url**

        The full url of the search page (including protocol). The page must contain an rss alternate link tag in the header for the saed search to work:

        ``<link rel="alternate" type="application/rss+xml" title="[page title]" href="[rss url of the search page]">``

        **username**

        The API username unique to your organization.

        **api_key**

        The API key associated with the above username
    * - Optional Parameters
      - **callback**

        If this parameter is provided, then the response will be returned as JSONp instead of JSON
    * - Response Format
      - **JSON**

        {"email": "[provided email]", "frequency": "D", "new_search": [true|false]}

        **JSONp**

        callback({"email": "[provided email]", "frequency": "D", "new_search": [true|false]})
    * - Response Values
      - **email**

        The email address for which the saved search was created

        **frequency**

        The frequency with which the saved search will be sent. Currently, the API only supports daily frequencies.

        **new_search**

        Returns true if this is a new search and false if the saved search already exists. My.jobs will not allow duplicate searches to be setup.

About this Document
===================

This document outlines the basic usage, but is not a comprehensive document for all features and uses. The services outlined in this document are provided as is. This document is produced and distributed by DirectEmployers Association (http://directemployers.org).
