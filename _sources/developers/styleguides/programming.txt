=================
Programming Guide
=================

Goal of this Guide
==================

This guide provides a common framework for collaboration amongst developers.
They serve as a foundation, not a strict set of rules. If conflict between
collaboration and this guide arise, always fall on the side of collaboration.

Third Party Code
================

We need to determine the rules of use for non-DE code in our projects. This is
a placeholder section until that work is done.


Universal Guides
================

Regardless of the language used, there are certain aspects that should be the
same across all platforms.  When documenting and formatting code you should be
able to answer yes to all of these questions:

- Can someone else read and understand this code without my help?
- Will I be able to understand this code in 12 months when I need to make a an
  edit?
- Does my code follow DRY principles?
- Will the code I just wrote cause problems for someone else?
- Will this code open a security hole in the application?


Updating Legacy Code
--------------------

When you are updating a legacy function or piece of code that was written prior
to these guidelines going into effect, do your best to bring that function up
to the documentation standard. However, do not edit code for the sole purpose
of formatting to match this guide.

Secure Coding
-------------

When adding or editing functionality, always keep in mind that outside forces
are trying to break into our systems. All effort should be made to maintain the
security and confidentiality of member and customer data, and to actively
prevent unauthorized access to our servers. This includes, but isn’t limited
to:

- Testing

 - Test on non-production environments
 - Test all code prior to release
 - Every method should have a unit test
 - Every issue should be QC’s by its reporter in a QC environment

- Deployment

 - All deployed code should be tested
 - Deployment should not take down servers in order to proceed
 - Deployments should be able to be rolled back to the last operational code
   branch if they fail

- Security of Environments

 - Access to Production Environments

  - Non cloud windows servers

   - Accessible only from within the office network or VPN

  - Cloud Servers & all Linux servers

   - Secured by SSH keys

 - Access to QC & Staging environments

  - Same as production, but shared login is allowed

References: OWASP Secure Coding Quick Reference Guide:
https://www.owasp.org/images/0/08/OWASP_SCP_Quick_Reference_Guide_v2.pdf

Code Documentation
------------------

When documenting code, code with assumption that you will not be the next
developer to work on the method. Be concise, but descriptive. Well written code
is not its own documentation. You must document your methods.

Standards to follow except for the cases that follow:

- Multiline Comments (eg Docstrings in Python, Delimited comments in C#)

 - Multiline comments should begin with a line break.
 - This is an exception to the Pep257 Python convention
  
 - Examples:

  ::

    /*
    This is line 1 of the comment.
    this is line two of the comment.

    */

  ::

    “””
    This is line 1 of the comment.

    This is line two of the comment. It can span 
    multiple lines for documentation purposes.

    “””

- Argument notation

 - Use colons to denote arguments
 - This is an exception to the Pep257 convention of a double dash
 - Example:

  - ``:argument: description of the argument``

- Arguments to include:

 - Inputs (Arguments passed into the function)
 - Returns (What the function returns)
 - Writes/Modifies (If the function writes something to the screen or modifies
   some global value, denote it.)

Python & Django
===============

Pep8 Formatting
---------------

All code should make a reasonable attempt to follow pep-0008 standard, except
where it conflicts with practices outlined in the previous section.
http://www.python.org/dev/peps/pep-0008/

Pep257 Docstrings
-----------------
Documenting functions, method, classes, etc should follow the Pep-257 standard, except where it conflicts with practices outlined in the previous section:
http://www.python.org/dev/peps/pep-0257/


C#
==

Except where it conflicts with the above universal sections, follow the
Microsoft C# Coding Conventions:
https://msdn.microsoft.com/en-us/library/ff926074.aspx


Java
====
Except where it conflicts with the universal styling guides, follow the Google
Java Style Guide:
https://google.github.io/styleguide/javaguide.html


User Interface
==============

Mobile First
------------

When designing new UI screens, wireframes, and usage patterns, start with the
mobile view first.

Responsive Design
-----------------

Mobile and Desktop views should be accomplished using the same page. These
pages should be responsive the device resolution, adapting the display on
demand to the best user experience for the device. Under no circumstances
should a separate mobile site be used in lieu of responsive design.

Mobile
------
Anything under 800px in width should be considered mobile with a one handed
touch interface. Support for this display level is mandatory for all sites.

Tablet
------

Anything under 1024px in width should be considered a tablet device with two
handed touch interface. Support for this display level is optional for all
sites.

Desktop
-------

Anything at or over 1024px in width should be considered a desktop or laptop
with a standard mouse and keyboard interface. Support for this display level is
mandatory for all sites.

Buttonization of links
----------------------

For touch interfaces, all links should be converted to a button with a minimum
dimension of 45px.

Icons
-----

Use Fontawesome for icons. http://fortawesome.github.io/Font-Awesome/.

JavaScript
==========

External Standards
------------------

Unless otherwise noted, follow the the Google Javascript style guide:
https://google.github.io/styleguide/javascriptguide.xml

Object Oriented
---------------

Every effort should be made to write javascript in an object oriented manner

JavaScript Libraries
--------------------

jQuery and jQuery UI should be utilized as appropriate. Do not use other
javascript libraries without consulting the rest of the team.

Code location
-------------

Javascript should be placed in external, versioned files on the CDN.
Incorporate the version in the file name. When external files are not
practical, a ``<script>`` block may be used. Inline javascript is not allowed.
Instead, use elements IDs and event mapping.

HTML, CSS, and Browser Support
==============================

External Standards
------------------

Unless otherwise noted, all front end markup and css should follow the Google
Webmaster Format:
https://google.github.io/styleguide/htmlcssguide.xml

Browser Support
---------------

The following browsers and versions are supported and should be used for testing:

- Google Chrome:

 - Latest stable build

- Mozilla Firefox

 - Latest stable build

- Microsoft Internet Explorer

 - version 8.0 and newer

- Microsoft Spartan

 - Latest stable build
   
- Apple Safari

 - version 7 and newer

- All other browsers

 - All other browsers that are modern and HTML5 compliant should be supported,
   but no testing is required in them.

Page Structure
--------------

- Use the default structure included with bootstrap. Exceptions should be well
  defended.
- Structure should be entirely controlled by CSS.

HTML Layout
-----------

- Use HTML5 as much as possible
- Use <html>, <head>, and <body> tags

HTML Tables
-----------

- All tables should use the bootstrap striped table styles by default

- Tables should be used only for the display of tabular data.

- Use ``<th>`` for headers, not ``<td><b>``

- ``<tbody>``, ``<thead>``, etc are optional

HTML Selectors for CSS
----------------------

HTML elements should be selected in the following manner:

- element level

 - For global or mass local styling.

- class level

 - For targeting specific types of elements

- ID level

 - For targeting specific, once per page elements

Django Templates Formatting
---------------------------

- Indent all HTML according to parent/child relationships

 - All tabs should 4 space faux-tabs

- Django tags 

 - Follow div spacing and do not create additional tabbing
 - Create 1 line space for django logic so we can see the django tags

- Comment closing tags with class associated with tag

::

  <div class=”span4”>

      {% if searches %}

      <div class=”form-box”>
          <ul class=”search-list”>
              <li>searches</li>
          </ul>
      </div>{# /form-box #}

      {% endif %}

  </div>{# /span4 #}

CSS Documentation
-----------------

- Document large sections of related styles with a one line header comment.
- Document style rules as necessary, paying particular attention to complex
  selectors.

Naming Conventions
------------------

- Keep class and id names as short as possible but as long as needed
- Examples: 
- .nav not .navigation
- .class not .cls
- hyphen-case all class and id names
- sub elements should use the parent element and add a hyphen case qualifier

 - this-class

   - this-class-sub-item

Media Selectors
---------------
- Media selectors should always be loaded in descending order or relevance:

 - Global Styles
 - narrow @media
 - Even more narrow @media
 - most narrow @media

- Global style rules should never be added after a media selector unless there is a specific reason for doing so, This reason must be documented.

CSS Rule Location
-----------------

**Primary**  
  Every effort should be made to put all CSS into a linked external css file.

**Limited**  
  Style blocks in the html body itself. This should only be utilized when a
  linked css file isn’t practical, such as conditional styling. In those cases,
  every effort should be made to use conditional classes rather than a
  ``<style>`` section.
**Rarely (But never in most cases)**  
  Via the “style” attribute on an item. There are only time this should exist:
  Inside of email templates. Due to client variability, there is no guarantee
  that ``<style>`` blocks or <link> will be displayed. As such, inline style
  is the only reliable option. See
  http://kb.mailchimp.com/article/css-in-html-email for more information. If
  there is a need to manipulate appearance via javascript. In those cases,
  every effort should be made first to swap classes rather than modify css
  directly.

Version Control
===============

Except as Documented below, our development and deployment plan follows the Git Flow pattern:
http://scottchacon.com/2011/08/31/github-flow.html

Exceptions to Git Flow
----------------------
**We have a custom deployment pattern**

- See New Deployment Schedule

**Committing rules:**

- Commit often and liberally.
- Reference tickets in your commits. 
- Include the ticket ID at the end of your commit message.

 - Example: “This is that new feature. MS-123”.

- Be descriptive, but concise.
- Do not commit compiled or temp files (ie .pyc)
- Do not merge PRs if any of the following are true:

 - It is a pull request you initiated yourself.
 - It is not associated with a ticket number
 - Functions are not well documented (see above)
 - Tests have not passed

Remotes
-------
Remotes for Version Control should reside on GitHub or our Team Foundation
Server located on Visual Studio online. Each remote should have a master,
staging, and quality control branch.

Pull Requests and Merges
------------------------

Pull requests should be opened by the primary author and reviewed by at least one other developer not involved in the feature development.

Issue Tracking & Jira
=====================

Jira is used for long term tracking of modifications and for visibility into our processes by non technical people who need to see what we are doing. 

Ticket Status
-------------

See New Deployment Schedule
