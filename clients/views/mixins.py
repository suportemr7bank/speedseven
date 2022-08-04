"""
Client mixins

"""

from django.http import Http404
from accounts import roles as accounts_roles
from accounts.auth import mixins as auth_mixins
from common.views import mixins
from core import models as core_models


class ClientRoleMixin(auth_mixins.RoleMixin):
    """
    Require client role to access view
    """

    role = accounts_roles.Roles.CLIENT


class CompleteSignUpMixin(ClientRoleMixin,
                          mixins.PageMenuMixin):
    """
    Test if signup is completed
    """
    menu_template_name = 'clients/menu.html'

    skip_signup_test = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_signup_completed = False
        self.signup_context = dict()

    def get_context_data(self, **kwargs):
        """
        Insert signup complete in context
        """
        context = super().get_context_data(**kwargs)
        context['signup_completed'] = self.is_signup_completed
        context.update(self.signup_context)
        return context

    def _eval_signup_completed(self):
        """
        Check if signup is completed
        """

        client = getattr(self.request.user, 'client', None)
        client_test = client and self.request.user.client.registration_completed
        self.signup_context['registration_completed'] = client_test
        term = getattr(self.request.user, 'useracceptanceterm_set', None)

        bank_acc_set = getattr(self.request.user, 'bankaccount_set', None)
        bank_acc = None
        if bank_acc_set and bank_acc_set.exists():
            bank_acc =  bank_acc_set.filter(main_account=True).first()
            self.signup_context['bank_account'] = bank_acc

        client_test = client and self.request.user.client.registration_completed
        term = getattr(self.request.user, 'useracceptanceterm_set', None)

        term_test = term and term.filter(
            term__type=core_models.AcceptanceTerm.Type.PRIVACY_POLICY).exists()
        self.signup_context['term_acceptance_completed'] = term_test

        profile_test = self.request.user.investorprofile_set.exists()
        self.signup_context['profile_test_completed'] = profile_test

        self.is_signup_completed = client_test and term_test and profile_test

        return self.is_signup_completed

    def dispatch(self, request, *args, **kwargs):
        self.is_signup_completed = self._eval_signup_completed()
        if not self.is_signup_completed and not self.skip_signup_test:
            raise Http404()
        return super().dispatch(request, *args, **kwargs)
