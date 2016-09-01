====================
Deployment Checklist
====================

Summary
=======
Follow this checklist after every deployment to staging or production. This
checklist is intended to verify that critical and major functionality is operating
as intdended.

**IF YOU FIND AN ISSUE**, bring it to the attention of the my.jobs team lead
immediatly. They will make the determination if a hotfix or rollback is needed.


Microsites
==========

Check microsites in the following areas.
**GOAL**: Verify correct operation of network and company sites.

Network Integrity
-----------------

- http://www.my.jobs resolves
- http://www.my.jobs/jobs resolves
- http://seattle.jobs shows only Seattle Jobs
- http://florida.jobs shows only florida jobs
- http://canada.jobs shows only canadian jobs
- Spot check 5 job detail pages, check for markup issues or server errors
- Apply links correctly redirect


Company Microsite Integrity
---------------------------

- http://phillips66.jobs shows only phillips 66 jobs
- http://jobs.schwab.com/ shows only Charles Schwab jobs
- http://hyatt-boston.jobs shows only hyatt jobs in Boston and has correct branding
- Spot check 5 job detail pages, check for markup issues or server errors


Redirects Integrity
-------------------

- Apply links correctly redirect


Search
------

- Searching for a keyword returns correct results
- Searching for a location returns correct results
- Searching for both keyword and location returns correct results
- Keyword search terms can be removed in the sidebar
- Location search terms can be removed in the sidebar


Navigation
----------

- Topbar loads correctly with user information
- Topbar dropdowns work correctly
- Adding a filter in the side bar works
- Removing a filter in the side bar works
- Active filters and search terms both show in the sidebar correctly


Secure.my.jobs
==============

Check the secure platform in the following areas.
**GOAL**: Ensure authentication works, PRM is available, and all other tools work.

Authentication
--------------

- Login as non-staff employer and verify tools are available
- Logout and log back in to verify it works

PRM
---

- Partners are listed
- Communication records are displayed

Reports
-------

- A report can be successfully run

User Management
---------------

- User list displays
- Role list diplays
- Users can be edited
- Roles can be edited
- Invitations work

Profile
-------

- Profile displays
