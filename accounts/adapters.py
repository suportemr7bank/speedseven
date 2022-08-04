"""
    Adapters implementation
"""

from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.signals import user_signed_up
from django.conf import settings
from django.urls import reverse

from invitations.app_settings import app_settings

from . import roles

ROLE_LOGIN_REDIRECT = getattr(settings, 'ACCOUNTS_ROLE_LOGIN_REDIRECT_VIEW')


class RedirectAdapter(DefaultAccountAdapter):
    """
        Django invitation adapter can't be imported.
        This adapter redirects sign in admin and clients to distinct pages
    """

    def is_open_for_signup(self, request):
        if hasattr(request, 'session') and request.session.get(
                'account_verified_email'):
            return True
        elif app_settings.INVITATION_ONLY is True:
            # Site is ONLY open for invites
            return False
        else:
            # Site is open to signup
            return True

    def get_user_signed_up_signal(self):
        """ The same as in django-invitation adapter"""
        return user_signed_up

    def get_login_redirect_url(self, request):
        """ Redirect user according role"""
        user = request.user
        if user.is_authenticated:
            if ROLE_LOGIN_REDIRECT:
                role = roles.get_last_role(user)
                if role:
                    view = ROLE_LOGIN_REDIRECT.get(role, None)
                    if view:
                        return reverse(view)
        return '/'
