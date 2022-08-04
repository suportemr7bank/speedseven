"""
Pool account views
"""

from django.urls import path

from .views import IncomeOperationListView

# pylint: disable=invalid-name
app_name = 'pool_account'

urlpatterns = [
    path('conta-pool/rendimentos/',
         IncomeOperationListView.as_view(), name='income_operation_list'),
]
