from datetime import datetime

from django.conf import settings
from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, Http404
from django.template import RequestContext

from myblogs.forms import BlogEntryForm
from myblogs.models import BlogEntry
from mypartners.models import Tag
from myjobs.decorators import requires


@requires('create blog entry')
def create_blog_entry(request):
    """Create a new blog entry."""

    ctx = {}
    if request.method == "POST":
        form = BlogEntryForm(request.POST)

        if form.is_valid():
            try:
                site = settings.SITE
            except AttributeError:
                # I'm probably going to regret claiming this - Edwin, May 2016
                raise Http404("Blogs are only available on microsites.")

            data = form.cleaned_data
            data.update({
                'author': request.user,
                'site': site,
                'last_edited': datetime.now()
            })
            tags = data.pop('tags', [])
            blog_entry = BlogEntry.objects.create(**data)
            blog_entry.tags = tags
            ctx['blog_entry'] = blog_entry

    else:
        form = BlogEntryForm()

    ctx['form'] = form

    return render_to_response(
        'myblogs/create_blog_entry.html', ctx, RequestContext(request))

def view_blog(request):
    """View microsite's blog."""
    try:
        site = settings.SITE
        company = site.canonical_company
    except AttributeError:
        # I'm probably going to regret claiming this - Edwin, May 2016
        raise Http404("Blogs are only available on microsites.")

    blog_entries = BlogEntry.objects.filter(
        site=site, published_on__lte=datetime.now()).order_by(
            '-published_on')

    ctx = {
        'blog_entries': blog_entries
    }

    return render_to_response(
        'myblogs/view_blog.html', ctx, RequestContext(request))

def rss_feed(request):
    """RSS Feed for microsite blog."""
    try:
        site = settings.SITE
        company = site.canonical_company
    except AttributeError:
        # I'm probably going to regret claiming this - Edwin, May 2016
        raise Http404("Blogs are only available on microsites.")


class BlogFeed(Feed):
    title = "RSS Feed"
    link = "/rss/"
    description = "Latest blog posts for this microsite"

    def items(self):
        try:
            site = settings.SITE
            company = site.canonical_company
        except AttributeError:
            # I'm probably going to regret claiming this - Edwin, May 2016
            raise Http404("Blogs are only available on microsites.")

        return BlogEntry.objects.filter(
            site=site, published_on__lte=datetime.now()).order_by(
                '-published_on')

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.body

    def item_link(self, item):
        return reverse('view_blog')

