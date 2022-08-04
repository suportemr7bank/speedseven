"""
   Authentication and permissions mixins
"""


from constance import config
from django.contrib.auth.mixins import \
    LoginRequiredMixin as _LoginRequiredMixin
from django.contrib.auth.mixins import \
    PermissionRequiredMixin as _PermissionRequiredMixin
from django.http import Http404

from accounts import roles


class ConfigRequiredMixin(_PermissionRequiredMixin):

    """
    Include config (django-constance) data in permission check
    """
    # = {'variable': <value>, ...}
    config_required = None
    redirect_field_name = None

    def get_login_url(self) -> str:
        raise Http404

    def get_permission_required(self):
        return []

    def has_permission(self) -> bool:
        result = True
        if self.config_required:
            result = self.has_config_permissions()

        return result

    def has_config_permissions(self):
        """
        Check config (django-constance) permissions
        """
        for key, value in self.config_required.items():
            # config  imported from django constance
            attr_value = getattr(config, key, None)
            if attr_value is not None and attr_value != value:
                return False
        return True


class PermissionRequiredMixin(_PermissionRequiredMixin):
    """
    Include config (django-constance) data in permission check
    """
    # = {'variable': <value>, ...}
    config_required = None

    def has_permission(self) -> bool:

        result = super().has_permission()
        if not result:
            return False

        result = True
        if self.config_required:
            result = self._has_config_permissions()

        return result

    def _has_config_permissions(self):
        for key, value in self.config_required.items():
            attr_value = getattr(config, key, None)
            if attr_value is not None and attr_value != value:
                return False
        return True


class LoginRequiredMixin(_LoginRequiredMixin):
    """
    Same as parent.
    Only for future customization, if necessary
    """


class RoleMixin(LoginRequiredMixin):
    """
    Role to access view
    """

    role = None

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        else:
            if not roles.has_role(request.user, self.role):
                raise Http404()
        return super().dispatch(request, *args, **kwargs)
