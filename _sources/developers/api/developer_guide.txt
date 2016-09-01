==========
MyJobs API
==========

Required Headers
================

* HTTP_ACCEPT
    * json: "application/json"
    * jsonp: "text/javascript"
* HTTP_CONTENT_TYPE
    * "application/json"

SavedSearch
===========

endpoint: /api/v1/savedsearch/

Required Parameters
-------------------

* email
* url
* username
* api_key

Auto-populated Fields
---------------------

* frequency: 'D'
* day_of_week: None
* day_of_month: None
* user:
    * email is a username: that user
    * email is secondary: its owner
* label, feed: set to output of validate_dotjobs_url

Returns
-------

Success
~~~~~~~

callback({"email": "<input_email>", "frequency": "D",
          "new_search": true if user has search with this url else false})

Error
~~~~~

* No/incorrect username and/or api_key
    * Blank
* No email provided
    * callback({"email": "No email provided"})
* User with the email address does not exist
    * callback({"email": "No user with email <email> exists"})
* No url
    * callback({"url": "No .JOBS feed provided"})
* Invalid url
    * callback({"url": "This is not a valid .JOBS feed"})

User
====

endpoint: /api/v1/user/

Required Parameters
-------------------

* email

Auto-populated Fields
---------------------

* password: 8 alphanumeric chars, generated via make_random_password method of user manager; Does not use i, I, l, o, O, 0

Returns
-------

Success
~~~~~~~

callback({"email": "<email>", "user_created": true if user was created else false})

Error
~~~~~

* No/incorrect username and/or api_key
    * Blank
* No email
    * callback({"email": "No email provided"})

Examples
========

Requirements
------------

* curl package is installed
* A user exists and has an api key:

::

    $ ./manage.py shell
    > from myjobs.models import User
    > from tastypie.models import create_api_key
    > user = User.objects.get(email="your_email@example.com")
    > create_api_key(User, instance=user, created=True)

The api key is available as user.api_key.key

Saved Search
------------

::

    $ curl -H "CONTENT-TYPE: application/json" -H "ACCEPT: text/javascript" “localhost:8000/api/v1/savedsearch/?username=<api email>&api_key=<user’s api key>&email=<existing email or secondary email>&url=www.my.jobs/jobs/?q=c%23

    # response if user is valid and search does not exist:
    ‘callback({“email”: “<existing email or secondary email>”, “frequency”: “D”, “new_search”: true})’

User
----

Warning: This creates an account and sends a confirmation email if it didn't exist

::

    $ curl -H "CONTENT-TYPE: application/json" -H "ACCEPT: text/javascript" “localhost:8000/api/v1/user/?username=<api email>&api_key=<user’s api key>&email=<new or existing email address>”

    # response if user does not exist:
    ‘callback({“email”: “<new email address>”, “user_created”: true})’

TBD
===

**Key Security**

Possibilities:
* Include user/key in JavaScript; Only accept posts from .JOBS domains
* Post to a view that adds header information
