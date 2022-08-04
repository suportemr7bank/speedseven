"""
Client operations views
"""

from django.urls import reverse_lazy
from investment.interfaces.views import ApplicationDepositBaseView, ApplicationWithdrawBaseView
from investment.views.operations import MoneyTransferBaseListView
from clients.views.mixins import CompleteSignUpMixin


class ClientDepositView(CompleteSignUpMixin, ApplicationDepositBaseView):
    """
    Client deposit view
    """
    success_url = reverse_lazy('clients:start_page')
    cancel_url = success_url


class ClientWithdrawView(CompleteSignUpMixin, ApplicationWithdrawBaseView):
    """
    Client withdraw view
    """
    success_url = reverse_lazy('clients:start_page')
    cancel_url = success_url


class MoneyTransferListView(CompleteSignUpMixin, MoneyTransferBaseListView):
    """
    Client account operations view
    """

    def get_queryset(self):
        return super().get_queryset().filter(application_account__user=self.request.user)
