import json
import logging

from django.core.exceptions import SuspiciousOperation
from django.conf import settings
from django.http import Http404, HttpResponse

from django.views.generic import View
from django.views.decorators.csrf import (
    csrf_exempt as django_csrf_exempt)

from myjobs.autoserialize import autoserialize
from myjobs.cross_site_verify import cross_site_verify
from universal.decorators import restrict_to_staff
from myblocks.models import Page, Block

logger = logging.getLogger(__name__)


class BlockView(View):
    page = None
    page_type = None

    def get(self, request, *args, **kwargs):
        return self.handle_request(request, *args, **kwargs)

    def handle_request(self, request, *args, **kwargs):
        if not self.page:
            self.set_page(request)
        required_redirect = self.page.handle_redirect(request, *args, **kwargs)
        if required_redirect:
            return required_redirect
        return HttpResponse(self.page.render(request))

    def post(self, request, *args, **kwargs):
        self.set_page(request)
        for block in self.page.all_blocks():
            # Checks to see if any blocks need to do any special handling of
            # posts.
            if hasattr(block, 'handle_post'):
                response = block.handle_post(request, **kwargs)
                # Some blocks redirect after appropriately handling posted
                # data. Allow the blocks to successfully redirect if they do.
                if response is not None:
                    return response

        return self.handle_request(request, *args, **kwargs)

    def set_page(self, request):
        """
        Trys to set the page for this site by:
            1. If the user is staff, getting a staging page for the specific
                site matching the page_type.
            2. Getting a page for the specific site matching page_type.
            3. Getting a page for the default site matching this page_type.
            4. Giving up and returning a 404.

        """
        if request.user.is_authenticated() and request.user.is_staff:
            try:
                page = Page.objects.filter(sites=settings.SITE,
                                           status=Page.STAGING,
                                           page_type=self.page_type)[0]
                setattr(self, 'page', page)
            except IndexError:
                pass

        try:
            page = Page.objects.filter(sites=settings.SITE,
                                       status=Page.PRODUCTION,
                                       page_type=self.page_type)[0]
        except IndexError:
            try:
                page = Page.objects.filter(sites__pk=1,
                                           status=Page.PRODUCTION,
                                           page_type=self.page_type)[0]
            except IndexError:
                raise Http404("myblocks.views.BlockView: Page object does not "
                              "exist")
        setattr(self, 'page', page)


# The django csrf exemption should stay first in this list.
@django_csrf_exempt
@cross_site_verify
@autoserialize
def secure_blocks(request):
    """
    Attempt to retrieve blocks objects for all items in the blocks element of
    the request body. secured by cross site verification wrapper. Currently
    restricted for non-staff users

    :url: /secure-blocks/
    :param request: ajax request potentially containing array of element ids for blocks
    :return: dictionary containing all matched blocks or Suspicious Operation (400)

    """
    blocks = {}
    try:
        if request.method == 'POST':
            loaded = json.loads(request.body) or {}
            blocks = loaded.get('blocks', {})
        elif request.GET.get('blocks', None):
            blocks = json.loads(request.GET.get('blocks', {}))
    except ValueError:
        message = ('secure block parse error: %r %r' %
                   (request.body,
                    request.GET))
        raise SuspiciousOperation(message)

    response = {'cookies':[]}

    for element_id in blocks:
        block = Block.objects.filter(element_id=element_id).first()
        if block is None:
            logger.warn("Failed block lookup: %s", element_id)
        else:
            try:
                block = block.cast()
                rendered = block.render_for_ajax(request, blocks[element_id])
                response[element_id] = rendered
                response['cookies'].extend(
                    block.get_cookies(request, **blocks[element_id]))
            except Exception as ex:
                logger.warn("Error loading widget: %s" % ex.message)

    return response
