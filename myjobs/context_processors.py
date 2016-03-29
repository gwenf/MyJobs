from django.conf import settings
from django.contrib.sites.models import Site


def current_site_info(request):
    """Retrieves site info from djang.contrib.sites

    Adds the following to the context:

    site_name -- the site name
    site_domain -- the site's domain
    description -- gives the site a description
    keywords -- key words for SEO
    """

    try:
        current_site = Site.objects.get_current()
        values = {
            'domain': current_site.domain,
            'site_name': current_site.name,
            'description': 'My.jobs is a platform that was designed to make' \
                        ' finding employment easier. Job seekers can control their data' \
                        ' making it easy for them to connect to like minded and' \
                        ' interested employers.',
            'keywords': 'jobs,job,find job,my jobs,job search,employment,employers,saved search,search agent',
        }
        return values
    except Site.DoesNotExist:
        # Return empty strings in case template needs context vars
        values = {'site_domain':'', 'site_name':'', 'description':'', 'keywords':'',}
        return values


def absolute_url(request):
    values = {
        'ABSOLUTE_URL': settings.ABSOLUTE_URL
    }
    return values


def webpack_dev_setting(request):
    """
    Used in templates that need to use webpack-dev-server in development.

    Don't set the setting in default_settings.py as it should remain off in
    production.

    i.e. Docker machine users probably want this:
    WEBPACK_DEV_SERVER_BASE_URL = 'http://secure.my.jobs:8080'

    Linux users probably want something like this:
    WEBPACK_DEV_SERVER_BASE_URL = 'http://10.10.12.999:8080'

    Linux users need an IP reachable by Modern IE VMs etc.
    """
    return {
        'wp_base_url': settings.WEBPACK_DEV_SERVER_BASE_URL,
    }
