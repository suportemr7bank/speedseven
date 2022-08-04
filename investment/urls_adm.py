"""
Investment admin views
"""

from django.urls import path, include

from .interfaces import views

from .views import application, application_model, operations

# pylint: disable=invalid-name
app_name = 'investment'

urlpatterns = [

    # Applications
    path('investimentos/aplicacoes/',
         application.ApplicationListView.as_view(), name='application_list'),
    path('investimentos/aplicacoes/novo/',
         application.ApplicationCreateView.as_view(), name='application_create'),
    path('investimentos/aplicacoes/editar/<int:pk>/',
         application.ApplicationUpdateView.as_view(), name='application_update'),
    path('investimentos/aplicacoes/configuracoes/<int:pk>/',
         views.ApplicationSettingsView.as_view(), name='application_settings'),

    # Rendimentos
    path('investimentos/aplicacoes/operacoes/<int:pk>/',
         views.ApplicationOperationView.as_view(), name='application_operation'),

    # Applications accounts
    path('investimentos/aplicacoes/contas/',
         application.ApplicationAccountListView.as_view(), name='applicationaccount_list'),
    path('investimentos/aplicacoes/contas/novo/',
         application.ApplicationAccountCreateView.as_view(), name='applicationaccount_create'),
    path('investimentos/aplicacoes/configuracoes/<int:pk>/',
         views.ApplicationSettingsView.as_view(), name='application_settings'),
    path('investimentos/aplicacoes/contas/configuracoes/<int:pk>/',
         views.ApplicationAccountSettingsView.as_view(), name='applicationaccount_settings'),

    # Applications operations
    path('investimentos/operacoes/extrato/',
         application.ApplicationOpListView.as_view(), name='applicationop_list'),
    path('investimentos/operacoes/aporte/<int:pk>/',
         operations.DepositView.as_view(), name='deposit_create'),
    path('investimentos/operacoes/retirada/<int:pk>/',
         operations.WithdrawView.as_view(), name='withdraw_create'),
    path('investimentos/operacoes/encerramento/<int:pk>/',
         operations.CloseApplicationView.as_view(), name='application_close'),
    path('investimentos/operacoes/transferencias/',
         operations.MoneyTransferListView.as_view(), name='moneytransfer_list'),
    path('investimentos/operacoes/agendamentos/',
         operations.AccountOpScheduleListView.as_view(), name='accop_schedule_list'),

    # Applications interface operations
    path('investimentos/operacoes/solicitacao/aporte/<int:pk>/',
         views.ApplicationDepositView.as_view(), name='deposit_request_create'),
    path('investimentos/operacoes/solicitacao/resgate/<int:pk>/',
         views.ApplicationWithdrawView.as_view(), name='withdraw_request_create'),
    path('investimentos/operacoes/aprovacao/<int:pk>/',
         views.ApplicationApprovalView.as_view(), name='moneytransfer_approval'),
    path('investimentos/operacoes/finalização/<int:pk>/',
         views.ApplicationCompletionView.as_view(), name='moneytransfer_completion'),

    # Application model
    path('investimentos/aplicacoes/modelo/',
         application_model.ApplicationModelListView.as_view(), name='applicationmodel_list'),
    path('investimentos/aplicacoes/modelo/novo/',
         application_model.ApplicationModelCreateView.as_view(), name='applicationmodel_create'),
    path('investimentos/aplicacoes/modelo/editar/<int:pk>/',
         application_model.ApplicationModelUpdateView.as_view(), name='applicationmodel_update'),

    path('investimentos/aplicacoes/', include('investment.applications.pool_account.urls')),

    path('investimentos/aplicacoes/', include('investment.applications.crowdfunding.urls')),


]
