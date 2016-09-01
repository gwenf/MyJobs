.. _secure-blocks-reference:

===============
Secure Blocks
===============

Secure Blocks are blocks retrieved via an AJAX call to an API. These blocks are
small reusable components that can be added to any webpage that is tied to a
secure (log in enabled, https) webpage.

Cross Site Verify
=================

Cross Site Verification was designed to satisfy the need for innumerable https
certificates in order to supply user information for display on various
microsites. With this solution, one secure site can manage user information for
multiple child sites.

For cross site verification to work, a nonsecure site (http) must be the child
site of a secure site (https). When a cross site API call is made via CORS or
JSONP, the parent site verifies the request to ensure the origin of the call
is from a valid child site. If the microsite does not have a parent site and
is a secure site, it makes the call to and returns from itself.

.. autofunction:: myjobs.cross_site_verify.cross_site_verify

.. autofunction:: myjobs.autoserialize.autoserialize

Secure Blocks Widgets
=====================

Within a microsites page, a div can be created with a special data attribute
(data-secure-block-id). This tag indicates that the value of that data
attribute is tied to a secure block element_id. That secure block's template
will then be rendered by the parent site and returned to the div. One API
call is made to the parent of the microsite (or itself, if it has no parent)
to retrieve all secure blocks divs. The request is subject to the cross site
verification step above.

.. autofunction:: myblocks.views.secure_blocks

.. autoclass:: myblocks.models.SecureBlock
    :members:

Testing a Secure Block Widget
------------------------------

To test a secure block widget, do the following:

* Navigate to Django Admin

* If parent site relationship is not set up, do the following:

 * Navigate to SeoSite, edit desired child site (currently my.jobs)

 * Under "parent_site" drop down, select desired parent site (secure.my.jobs)

 * Save

* Navigate to the active site configuration for the child site

 * Check the box labled 'Use secure blocks'

 * Save

* Locate the correct model under MyBlocks (ex. SavedSearchWidgetBlock)

* Add new block

 * The only important fields are element_id and template. Template will be
   automatically populated with a default template.
   Offset and Span are required, but currently have no effect on
   the widget. These can be set to 0

 * Widget IDs are currently hardcoded on templates. Therefore, the element IDs
   for secure block widgets are predetermined. The two widget element IDs
   included in microsites templates are..

  * saved_search for saved search widget

  * sb_toolbar for toolbar/topbar

  * If an element ID other than these two is used, it must also be included
    in a template for display using the following format

   * `<div data-secure_block_id="--YOUR ELEMENT ID--"></div>`

* This will only work on templates loaded from seo_base.html

* All secure blocks widgets that replace existing functionality (saved search,
  tools) will REPLACE their counterparts if secure-blocks is enabled for that
  site.

secure-block.js
---------------

Secure Blocks relies on the file secure-block.js file located in the
static directory. This file handles creating the ajax call based on the secure
block ids as well as populating the respective divs with the response.

**jQuery Data Attributes**:
jQuery Data attributes assigned to the same div as the data-secure-block-id div
will be sent to the secure blocks API in a dictionary form. Below is an example
of a webpage with one secure block named test that has data attributes email
and url.

.. code:: javascript

    {'test': {email:'test@example.com', url:'www.example.com'}}

The data attributes will then be available as context variables in the secure
blocks template.

.. note:: jQuery converts hyphens to camelCase when sending data attributes.
    The data attribute email-address would resolve in the secure block template
    as emailAddress. This does not affect underscores (email_address
    is email_address)

**Main Functions**

    **function load_secure_blocks(dashboard_url) { ... }**

        *Request secure blocks for all divs containing data-secure-block-id*

        :dashboard_url: The URL of the secure parent of the microsite


    **function reload_secure_block(block_id, callback) { ... }**

        *Request specific secure block to be reloaded*

        :block_id: Block to be reloaded

        :callback: Function to be called after ajax call completes successfully

.. _saved-search-widget:

Saved Search Widget
===================

The Saved Search widget is the first of the secure-blocks widgets to have
complex functionality. It incorporates Javascript, CSS, and HTML.

.. autoclass:: myblocks.models.SavedSearchWidgetBlock
    :members:

The appearance of the widget is largerly based on the template saved into the
model. There are template tags representing the various states that the widget
can be in.

As of this writing, the only javascript file used in the widget is
static/saved-search.js . This file contains the logic for calling the Saved
Search API and refreshing the

The current anchor for saved search is as such:

`<div data-secure_block_id="saved-search"></div>`

Tools Widget
============

The tools widget represents the same functionality as the legacy topbar widget.
This is the first widget to rely on an additional data element, data-widget_type
to prevent the legacy topbar from being loaded in addition to the tools secure
block.

The current anchor for the tools widget is as such:

`<div data-secure_block_id="sb_toolbar" data-widget_type="tools"></div>`
