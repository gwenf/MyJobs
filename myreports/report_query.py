"""Manage queries associated with report types.

This module contains query handlers and utilities for organizing and finding
them by name. The presumption in this module is that there is a list of named
report types in the database. We associate handlers by those names here.

A handler is repsponsible for:
    * generating an appropriate query set
    * converting records to plain python dictionaries and lists, suitable for
      conversion to json.
    * generating a list of available columns

See Also: get_report_query and @report_query.

Example:

>>> @report_query("PRM")
>>> class PRMReportType(object):
        fields = ['name', 'email', 'locations', ...]

        def report_query_set(self, company):
            # return a queryset.
            # Include any prefetch_related optimizations here.
            pass

        def extract(self, rec):
            # rec is a model. Returns a dict.
            # Handle any foreign key expansion in this method.
            pass


>>> get_report_query("PRM")
# returns reference to class PRMReportType

"""
from mypartners.models import Status, Contact


report_queries = {}


def report_query(report_query_name):
    """Register this class as a report query handler.

    See also module report_query for interface.
    """
    def register(report_query):
        report_queries[report_query_name] = report_query
        return report_query
    return register


def get_report_query(report_query_name):
    """Return the class associated with this query name."""
    return report_queries[report_query_name]()


def list_of_str(qs):
    return [unicode(f) for f in qs.all()]


@report_query("Contacts")
class ContactReportType(object):
    fields = ['name', 'email', 'phone', 'locations', 'tags', 'notes']

    def report_query_set(self, company):
        qs = (Contact.objects.filter(partner__owner=company)
              .prefetch_related('locations', 'partner')
              .filter(approval_status__code__iexact=Status.APPROVED))
        return qs

    def extract(self, rec):
        result = dict((f, unicode(getattr(rec, f, None)))
                      for f in self.fields)
        result['tags'] = list_of_str(rec.tags)
        result['locations'] = list_of_str(rec.locations)
        result['notes'] = list_of_str(rec.locations)
        result['partner'] = rec.partner.name
        return result
