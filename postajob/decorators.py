from functools import partial
from django.conf import settings
from universal.decorators import not_found_when, warn_when

def site_misconfigured(request):
    try:
        return not settings.SITE.canonical_company.has_packages
    except AttributeError:
        return True

error_when_site_misconfigured = partial(
    not_found_when,
    condition=site_misconfigured,
    message='Accessed company owns no site packages.')

error_when_company_missing_from_sitepackages = partial(
    not_found_when,
    condition=lambda req:
    not req.user.is_anonymous()
    and not req.user.can_access_site(settings.SITE),
    message="This site is not part of a site package owned by a company user "
            "has access to.")


