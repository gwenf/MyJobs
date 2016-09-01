=================
Non User Outreach
=================

Non User Outreach is a set of modules used to track outreach efforts made by
members of a company who are not primary contacts in a company's outreach
program. These outreach efforts are tracked by emails sent to dedicated inboxes
on the my.jobs platform, and are then reviewed and converted into contact,
partner, and contact record objects by a authorized user for a given company.

==============
Conversion API
==============

This API is designed to accept form info derived from a non user outreach
record. When a non user outreach record is reviewed and modified, this API
handles the creation of relevant objects and the tracking of workflow status
of the non user outreach record.

A total of three activities are required for full API use.

**convert outreach record**

This allows use of the API.

**create contact**

Allows the API to create a contact. Otherwise, it can only link a contactrecord
to an existing contact.

**create partner**

Allows the API to create a partner. Otherwise, it can only link a contactrecord
to an existing partner.


url: `POST /prm/api/nonuseroutreach/records/convert`

Sample API Data Object

.. code:: python

    {
        "outreachrecord":{"pk":"1", "current_workflow_state":"47"},

        "partner": {"pk":"", "name":"James B", "data_source":"email", "uri":"http://www.example.com",
        "tags":["12", "68"]},

        "contacts": [{"pk":"", "name":"Nicole J", "email":"nicolej@test.com", "phone":"7651234123",
        "location":{"pk":"", "address_line_one":"", "address_line_two":"",
        "city":"Newtoneous", "state":"AZ", "country_code":"1",
        "label":"new place"}, "tags":["54", "12", "newone"],
        "notes": "long note left here"}, {"pk":"", "name":"Markus Johnson",
        "email":"markiej@test.com", "phone":"1231231234",
        "location":{"pk":"", "address_line_one":"boopie", "address_line_two":"",
        "city":"Blampitity", "state":"NY", "country_code":"1",
        "label":"newish place"}, "tags":["54", "12", "newone"],
        "notes": "another long note left here"}],

        "contactrecord": {"contact_type":"phone", "location":"dining hall", "length":"10:30",
        "subject":"new job", "date_time":"2016-01-01 05:10", "notes":"dude was chill",
        "job_id":"10", "job_applications":"20", "job_interviews":"10", "job_hires":"0",
        "tags":["10", "15", "3"]}
    }

Sample API Error Return Object

.. code:: python

    {
        "api_errors": [],
        "form_errors":
        {
            "partner": [],
            "contact": [],
            "outreachrecord": [{"message": "invalid outreach record pk"}],
            "contactrecord": [{"field": "date_time",
            "message": ["'2016-01-01 aa05:10' value has an invalid format. It must be in YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ] format."]}]
        }
    }

