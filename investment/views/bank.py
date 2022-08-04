"""
Bank views
"""

from common.views import generic, mixins
from core import workflow

from .. import models, forms


class BankAccountViewMixin:
    """
    User bank account mixin

    """
    model = models.BankAccount
    form_class = forms.BankAccountForm
    title = 'Conta bancária'

    def get_form_kwargs(self):
        """
        Adding user to form
        """
        kwargs = super().get_form_kwargs()
        user = self.request.user
        if user.is_superuser:
            kwargs['user'] = self.object.user if self.object else None
        else:
            kwargs['user'] = user
        kwargs['operator'] = user
        return kwargs


class BankAccountBaseListView(BankAccountViewMixin,
                              mixins.ListViewMixin):
    """
    Client bank account list
    """

    model = models.BankAccount
    template_name = 'common/list.html'
    title = 'Dados bancários'


class BankAccountCreateView(BankAccountViewMixin,
                            workflow.ApprovalWorkflowViewMixin,
                            generic.CreateView):
    """
    Client bank account create
    """

    template_name = 'common/form.html'


class BankAccountUpdateView(BankAccountViewMixin,
                            workflow.ApprovalWorkflowViewMixin,
                            generic.UpdateView):
    """
    Client bank account update
    """

    template_name = 'common/form.html'
