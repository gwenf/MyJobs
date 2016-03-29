====================
Postajob Setup Guide
====================

This guide describes how to configure a microsite to use the ``postajob``
application in a variety of use cases. We discuss first the common requirements
among each use case, then describe the specific use cases in detail.

For your own purposes, you should change this URL to the one used by your
microsite.

Conventions used in this guide
==============================
To make the various use cases more concrete, this guide has adopted a number of
conventions to assist you in your understanding of various concepts:

- When we talk about a site, we will always use http://directemployers.jobs.
  This ensures that there is always a live example for you to compare to the
  site you are attempting to configure.

- In production, it is more likely that custom-tailored roles will be created
  for each of the personas that might be assumed when performing various tasks
  on a microsite with postajob enabled. However, for simplicity, we always
  assign our user the ``Admin`` role, which automatically includes every
  activity available in the system.

- The above might make it difficult to ascertain whether a page is working as
  expected. Thus, with each use case description, this guide provides a table
  which annotates which activities are required for each of the views relevant
  to the use case being examined.

Requirements
============

Each use case has a different set of requirements. As some of those
requirements are shared between some of the use cases, we've decided to collect
the instructions for each of those requirements in one spot. When you are
reading use case descriptions, the requirements will be listed as well. As
such, feel free to go directly to the :ref:`use cases <use-cases>` and refer
back to these requirements when necessary.

.. _enable-login:

Logging In
----------

A lot of postajob features requires that a user be logged in. As most sites
aren't network sites (and thus do not have a top bar with a login link), they
don't have a built in way for users to log in, which is where login blocks come
in. Creating a login page can be done as follows:

From the Django shell
'''''''''''''''''''''

Find the site you wish to add a login page to::

>>> from seo.models import *
>>> from myblocks.models import *
>>> site = SeoSite.objects.get(domain="directemployers.jobs")

Add a page to that site::

>>> page = Page.objects.create(name="DirectEmployers Login Page", page_type=Page.LOGIN)
>>> page.sites.add(site)

Add a row containing a login block to that page::

>>> row = Row.objects.create()
>>> row_order = RowOrder.objects.create(row=row, page=page, order=0)
>>> login_block = LoginBlock.objects.create(name="DirectEmployers Login Block", offset=0, span=12")
>>> block_order = BlockOrder.objects.create(block=login_block, row=row, order=0)

From the Django admin
'''''''''''''''''''''

.. note:: Setting offset to 0 and span to 12 would have the effect of creating
          a content block which fills the width of its parent.

#. `create a new login block`_, ensuring to select an element id, offset, and
   span. 
#. `create a new row`_ and add your new login block to it. Be sure to assign an
   order to it, noting that indexes start at 0, not 1.
#. `create a new page`_ tied to the `SeoSite` you are working with, using
   'Login Page' as the page type. As with row, be sure to add an order.

You should now be able to visit the `login page`_ for your microsite.

.. _enable-posting:

Enabling Job Posting
--------------------
Enabling job posting is a matter of granting a particular company access to the
posting application and then assigning a particular user a role with activities
related to job posting. Specifically, you need to:

  - associate a company with your microsite

  - give that company app-level access to posting

  - assign the user trying to access job posting a role with the correct
    activities

From the Django shell
'''''''''''''''''''''

Associate the company to the seo site::

>>> from seo.models import *
>>> company = Company.objects.get(name="DirectEmployers Association")
>>> site = SeoSite.objects.get(domain="directemployers.jobs")
>>> site.canonical_company = company
>>> site.save()

Enable Posting access for the company::

>>> from myjobs.models import *
>>> posting_access = AppAccess.objects.get(name="Posting")
>>> company.app_access.add(posting_access)

Associate the user to the company::

>>> role = company.role_set.get(name="Admin")
>>> user = User.objects.get(email="dev@apps.directemployers.org")
>>> user.roles.add(role)

From the Django Admin and User Management Tool
''''''''''''''''''''''''''''''''''''''''''''''

#. select the appropriate company as the ``canonical_company`` for 
   `your seo site`_.
#. `enable posting access` for the company chosen above by adding "Posting" to
   the "Chosen App-Level Access" box in the "App-Level Access" section.
#. `assign your user a role` which has permission to post.

   .. note:: 

     - at the moment, this must be done on https://secure.my.jobs as that is
       the only domain for which User Management is available

     - be sure to change to the correct company in the topbar.

.. _create-sitepackage:

Creating a Site Package
-----------------------
.. note:: 
  The jobs within products are posted to sites within site packages owned by
  the company who owns the product, *not* the company who purchased the
  product.

The microsites on which a job will be posted to is determined by the site
package (not to be confused with site familiess) associated with the compnay
who owns the job. Creating a site package is straight forward.


From the Django Shell
'''''''''''''''''''''

Obtain the company who will own the site package::

>>> from seo.models import *
>>> company = Company.objects.get(name="DirectEmployers Association")

Find relevant sites::

>>> sites = SeoSite.objects.filter(canonical_company=company)

Associate the company and sites to a new site package::

>>> site_package = SeoSite.objects.create(name="DirectEmployers Sites, owner=company)
>>> site_package.sites = sites

From the Django Admin and User Management Tool
''''''''''''''''''''''''''''''''''''''''''''''
`Create a new site package`, being sure to:
  
  - name it something meaningful (eg. DirectEmployers Sites)

  - only select sites affiliated with the company who owns the job

  - select that company as the site package's owner

.. _enable-marketplace:

Enabling the Marketplace
------------------------
Enabling the marketplace is similar to `enabling job posting <enable-posting>`
except that you need to grant marketplace access instead of posting access, and
you need to add marketplace activities to a user's role instead of posting
activities. All together then, you need to:

  - associate a company with your microsite

  - give that company app-level access to marketplace

  - assign the user trying to access the marketplace a role with the correct
    activities

From the Django Shell
'''''''''''''''''''''

Associate the company to the seo site::

>>> from seo.models import *
>>> company = Company.objects.get(name="DirectEmployers Association")
>>> site = SeoSite.objects.get(domain="directemployers.jobs")
>>> site.canonical_company = company
>>> site.save()

Enable MarketPlace access for the company::

>>> from myjobs.models import *
>>> marketplace_access = AppAccess.objects.get(name="MarketPlace")
>>> company.app_access.add(marketplace_access)

Associate the user to the company::

>>> role = company.role_set.get(name="Admin")
>>> user = User.objects.get(email="dev@apps.directemployers.org")
>>> user.roles.add(role)

From the Django Admin and User Management Tool
''''''''''''''''''''''''''''''''''''''''''''''

#. select the appropriate company as the ``canonical_company`` for 
   `your seo site`_.
#. `enable marketplace access` for the company chosen above by adding "Posting" to
   the "Chosen App-Level Access" box in the "App-Level Access" section.
#. `assign your user a role` which has permission to post.

.. _use-cases:

Use Cases
=========
Here, we describe the purpose of and setup requirements of each of the eight
postajob use cases.

Use Case 2: External party buying a job
---------------------------------------

Rebecca has a job that can't be indexed, as it is on an internal ATS that can't
be reached by DE's agents. She logs into post-a-job and posts the site to her
.JOBS Company Sites. The jobs appears. Later, she can come back and edit it or
delete it once it filled.

Requirements:

  - :ref:`enable-login`

  - :ref:`enable-posting`

Views
'''''

=================== ============= ===================
URL Path            View Name     Required Activities
=================== ============= ===================
/posting/all/       jobs_overview read job
/posting/job/add/   JobFormView   create job
/posting/job/update JobFormView   update job
=================== ============= ===================


Use Case 3: Site owner creating a product for sale
--------------------------------------------------
Paul logs into the posting admin. He creates a product for 5 job postings in 30
days. He then creates a group and assigns his new product to that group. The
group appears in the products for sale page that SBO sees when visiting Paul's
site. Later, he can edit or delete the posting as needed, but any purchased
instances of the product are unaffected.

Requirements:

  - :ref:`enable-login`

  - :ref:`enable-marketplace`

Views
'''''

=================================== ======================= ===================
URL Path                            View Name               Required Activities
=================================== ======================= ===================
/posting/admin/product              admin_products          read product
/posting/admin/product/add          ProductFormView         create product
/posting/admin/product/update       ProductFormView         update product
/posting/admin/product/group        admin_groupings         read grouping
/posting/admin/product/group/add    ProductGroupingFormView create grouping
/posting/admin/product/group/update ProductGroupingFormView update grouping
/posting/admin/product/group/delete ProductGroupingFormView delete grouping
=================================== ======================= ===================


.. _create a new login block: http://directemployers.jobs/admin/myblocks/loginblock/add/
.. _create a new row: http://directemployers.jobs/admin/myblocks/row/add/
.. _create a new page: http://directemployers.jobs/admin/myblocks/page/
.. _login page: http://directemployers.jobs/login
.. _your seo site: http://directemployers.jobs/admin/seo/seosite/36815/?_changelist_filters=q%3Ddirectemployers.jobs
.. _enable posting access: http://directemployers.jobs/admin/seo/company/999999/?_changelist_filters=q%3Ddirectemployers%2Bass
.. _enable marketplace access: http://directemployers.jobs/admin/seo/company/999999/?_changelist_filters=q%3Ddirectemployers%2Bass
.. _assign your user a role: https://secure.my.jobs/manage-users/#/users?_k=w22qot
.. _Ceate a new site package: https://secure.my.jobs/admin/postajob/sitepackage/add/
