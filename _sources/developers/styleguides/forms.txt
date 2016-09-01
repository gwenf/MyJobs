===================================
Forms: Layout and Input Type Usage
===================================

This guide covers the use of forms and specific input types. At the bottom of
the document is a sample image with input layout examples.

High Level Requirements
=======================
Form layouts should handle all layout widths automatically. For testing, this
includes two primary widths

**Wide**:
Used in layouts when the form is in a span 8.

**Narrow**:
Used in mobile layouts and when the form is in a span 4 (ie the side bar).

**Form Validation**:

* Validation errors should be able to stack when there are multiple errors
* Non field form errors should appear at the top of a form in a red alert
* All Validation warnings should preserve any input already entered in a form
* Validation warnings should replace any help text on the form
* Validation details (if applicable) should be hidden by default
 
Aligement
=========

**Wide Width**

* Labels should be in a span3 column to the left of the field they label
* Label text should be right aligned
* Required forms should use **bold** text
* Inputs should take the rest of the parent column width
* Inputs should be left aligned
* Buttons should be in the column with inputs
* Buttons should align left in a row
* Buttons should be ordered with most important to the left, least to the right

**Narrow Width**

* Labels should appear above the input they label
* Labels should be left aligned
* Inputs should take the full width of the column, less the margins

Field Validation
================

Changes made to a field in error:

* input border turns red
* label turns red
* help text is hidden (if applicable)
* a warning icon and error description are shown immediately below the fold. If
  there are multiple errors, each one gets its own line below the field
* if additional details are available for an error, they should be placed in a 
  hidden div below the error.
  
  * To access this div, a tree arrow would be placed aligned right on the 
    description row. This arrow toggles the div. 
  * The div should appear in the main DOM layer, not as a floating element.

Field Usage
===========

Text
----
* Standard text input by default
* Textarea for paragraph style input

Option List
-----------
* Select list
* Radio buttons only when it is appropriate

Locations
---------
* Select list for country
* Select list for region

  * default should be "Select Region..."
  * text field if there no json file available for selected country

Date
----
* Disabled text input with date picker
* date picker should include a select list for month and year to allow users to
  quickly find the date they want

Time
----
* set of three drop downs in sequence. 

  * Hours (1-12)
  * Minutes (0-59)
  * AM/PM

Booleans
--------
* Presented as a checkbox
* If multiple checkboxes are presented as one control, include a left aligned 
  label to the right of the checkbox

.. image:: ../../_static/forms.png
    :alt: form input usage examples