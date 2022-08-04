
"""
Admin bank views
"""

from django.urls import reverse_lazy
from common.views import mixins
from investment.views import bank
from investment import tables as invest_tables
from investment.forms import BankFilterForm


class BankAccountListView(mixins.AdminMixin,
                          BankFilterForm,
                          bank.BankAccountBaseListView):
    """
    Client bank account list
    """

    table_class = invest_tables.bank_account_table(
        'core:bank_account_update', exclude_owner=False)

    controls = [
        {'link': {'text': 'Novo', 'url': 'core:bank_account_create'}},
    ]


class BankAccountCreateView(mixins.AdminMixin,
                            bank.BankAccountCreateView):
    """
    Client bank account create
    """

    success_url = reverse_lazy('core:bank_account_list')
    cancel_url = success_url


class BankAccountUpdateView(mixins.AdminMixin,
                            bank.BankAccountUpdateView):
    """
    Client bank account update
    """

    success_url = reverse_lazy('core:bank_account_list')
    cancel_url = success_url
