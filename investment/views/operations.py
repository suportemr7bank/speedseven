"""
Aplication account operations views
"""

from django.urls import reverse_lazy

from accounts.auth import mixins as auth_mixins
from accounts import roles as accounts_roles
from common.forms import mixins as form_mixins
from common.messages import message_add
from common.views import generic, mixins
from investment import models

from .. import forms, tables
from ..models import ApplicationAccount


class OperationBaseView(mixins.AdminMixin, form_mixins.LoggedUserMixin, generic.FormView):
    """
    Base view for admin direct deposit and witdraw
    """

    success_url = reverse_lazy('investment:applicationaccount_list')
    template_name = 'common/form.html'
    cancel_url = success_url
    success_message = 'Depósito realizado com sucesso!'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        #pylint: disable=no-member
        kwargs['application_account'] = ApplicationAccount.objects.get(
            pk=self.kwargs['pk'])
        return kwargs

    def form_valid(self, form):
        # Form is not automatically saved
        form.save()
        message_add(self.request, self.success_message)
        return super().form_valid(form)


class DepositView(OperationBaseView):
    """
    View for make deposit
    """
    form_class = forms.DepositiForm
    title = "Aporte direto"
    success_message = 'Depósito realizado com sucesso!'


class WithdrawView(OperationBaseView):
    """
    View for make withdraw
    """
    form_class = forms.WithdrawForm
    title = "Retirada direta"
    success_message = 'Retirada realizada com sucesso!'


class CloseApplicationView(OperationBaseView):
    """
    View for make withdraw
    """
    form_class = forms.CloseApplicationForm
    title = "Encerrar aplicação"
    success_message = 'Aplicação encerrada com sucesso!'

    def get_controls(self):
        controls = super().get_controls()
        controls[1].text = "Encerrar aplicação"
        return controls


class MoneyTransferBaseListView(mixins.ListViewMixin):
    """
    Money transfer base
    """

    model = models.MoneyTransfer
    table_class = tables.MoneyTransferBaseTable
    template_name = 'common/list.html'
    title = 'Solicitações de aportes e resgates'


class MoneyTransferListView(mixins.AdminMixin, MoneyTransferBaseListView):
    """
    Money transfer
    """

    table_class = tables.MoneyTransferTable
    title = 'Solicitações de transferência'


class AccountOpScheduleListView(mixins.AdminMixin, mixins.ListViewMixin):
    """
    List of applications
    """
    model = models.AccountOpSchedule
    table_class = tables.AccountOpScheduleTable
    template_name = 'common/list.html'
    title = 'Agendamentos'


class ReceiptsView(auth_mixins.LoginRequiredMixin, generic.FileBaseView):
    """
    View to show/download operations receipts
    """

    model = models.MoneyTransfer
    field = 'receipt_file'
    media_file_root = 'private/receipts/'

    def can_access_file(self, request):
        user = request.user
        roles = [accounts_roles.Roles.ADMIN, accounts_roles.Roles.CLIENT]
        if accounts_roles.has_role_in(user, roles):
            return True
        return False
