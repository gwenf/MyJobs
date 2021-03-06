from django.db.models import Q
from ajax_select import register, LookupChannel
from seo import models

@register('companies')
class CompaniesLookup(LookupChannel):
    model = models.Company
    min_length = 3

    def get_query(self, q, request):
        return self.model.objects.filter(
            name__istartswith=q).order_by('name')[:10]

    def format_match(self, company):
        """
        Returns a string ot be used next to each company that displays how many
        admins belong to that company, or a warning if there aren't any.

        """
        template = "{name} ({count} users){warning}"
        count = company.admins.count()
        warning = "" if count else " **Might be a duplicate**"

        return template.format(name=company.name, count=count, warning=warning)


@register('sites')
class SitesLookup(LookupChannel):
    model = models.SeoSite
    min_length = 3

    def get_query(self, q, request):
        return self.model.objects.filter(
            domain__istartswith=q).order_by('domain')[:10]

    def get_objects(self, ids):
        return list(self.model.objects.filter(pk__in=ids))
