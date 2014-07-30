from functools import wraps

from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect

from myjobs.models import User
from universal.helpers import build_url, get_company


def company_has_access(perm_field):
    """
    Determines whether or not a user and their current company has access to
    the requested feature.

    inputs:
        :perm_field: The name of the BooleanField on Company that handles
            permissions for the requested feature.

    """
    def decorator(view_func):
        def wrap(request, *args, **kwargs):

            # If the user is not logged in, redirect them to the login page
            # with this url as the next url.
            if request.user.is_anonymous():
                params = {'next': request.path, }
                next_url = build_url(reverse('home'), params)
                return HttpResponseRedirect(next_url)

            # If the user is logged in, but they aren't a CompanyUser or they
            # are a CompanyUser, but their current Company doesn't have
            # perm_field access, return a 404.
            company = get_company(request)

            if not company or (perm_field and not getattr(company, perm_field,
                                                          False)):
                raise Http404

            return view_func(request, *args, **kwargs)
        return wraps(view_func)(wrap)
    return decorator


def activate_user(view_func):
    """
    Activates the user for a given request if it is not already active. The
    main use case for this is password resets, where the user must be active
    to successfully submit the request.
    """
    @wraps(view_func)
    def wrap(request, *args, **kwargs):
        if request.method == 'POST':
            email = request.POST.get('email', None)
            if email is not None:
                user = User.objects.get_email_owner(email)
                if user is not None and not user.is_active:
                    user.is_active = True
                    user.deactivate_type = 'none'
                    user.save()
        return view_func(request, *args, **kwargs)
    return wrap