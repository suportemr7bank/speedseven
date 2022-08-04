"""
Rest api helpers  (drf)
"""

from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from accounts import roles


def _check_roles(user):
    if settings.API_ENABLE_PRODUCTION_MODE:
        return roles.has_role(user, roles.Roles.APIAPP)
    else:
        return roles.has_role_in(user, [roles.Roles.APIACC, roles.Roles.APIAPP])


def api_user_authentication_rule(user):
    """
    Authorize only registered user with api role access
    """
    return user and _check_roles(user)


class ApiUserIsAuthenticated(IsAuthenticated):
    """
    Allows access only to authenticated users with  api access (APIACC) role.
    """

    def has_permission(self, request, view):
        user = request.user
        return super().has_permission(request, view) and _check_roles(user)
