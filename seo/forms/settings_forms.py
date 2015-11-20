from django import forms

from seo.models import SeoSite
from universal.forms import RequestForm
from universal.helpers import get_company_or_404


class SeoSiteSettingsForm(RequestForm):
    class Meta:
        model = SeoSite
        exclude = []


class EmailDomainForm(forms.Form):
    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request')
        company = get_company_or_404(request)
        self.sites = SeoSite.objects.filter(canonical_company=company)
        super(EmailDomainForm, self).__init__(*args, **kwargs)
        for site in self.sites:
            field_kwargs = {
                'widget': forms.Select(),
                'choices': site.email_domain_choices(),
                'initial': site.email_domain,
                'label': 'Email Domain For %s' % site.domain,
            }
            self.fields[str(site.pk)] = forms.ChoiceField(**field_kwargs)

    def save(self):
        for site in self.sites:
            if str(site.pk) in self.cleaned_data:
                new_domain = self.cleaned_data[str(site.pk)]
                site.email_domain = new_domain
                site.save()