
"""
     Urls
"""
from django.urls import path
from products.views import dashboards as core_dash_views

from .views import clients, dashboards, operations

# pylint: disable=invalid-name
app_name = 'clients'

urlpatterns = [
    path('inicio/', clients.StartView.as_view(), name='start_page'),

    path('cadastro/editar/',
         clients.ClientUpdateView.as_view(), name='client_update'),
    path('cadastro/termos-de-aceite/',
         clients.UserAcceptanceTermCreateView.as_view(), name='acceptance_term_create'),

    path('cadastro/perfil-de-investidor/',
         clients.InvestorProfileTestDetailView.as_view(), name='investor_profile_test_detail'),
    path('cadastro/perfil-de-investidor/novo/',
         clients.InvestorProfileTestCreateView.as_view(), name='investor_profile_test_create'),
    path('cadastro/perfil-de-investidor/editar/',
         clients.InvestorProfileTestUpdateView.as_view(), name='investor_profile_test_update'),

    path('cadastro/dados-bancarios/',
         clients.BankAccountListView.as_view(), name='bank_account_list'),
    path('cadastro/dados-bancarios/novo/',
         clients.BankAccountCreateView.as_view(), name='bank_account_create'),
    path('cadastro/dados-bancarios/editar/<int:pk>/',
         clients.BankAccountUpdateView.as_view(), name='bank_account_update'),

    path('produtos/', clients.ProductsView.as_view(), name='products_page'),
    path('produtos/contratar/<int:pk>',
         clients.ProductsPurchaseView.as_view(), name='products_purchase_page'),

    path('produtos/categorias/documentos/<int:pk>/',
         clients.CategoryDocumentDetailView.as_view(), name='category_document_detail'),


    path('broker/', clients.BrokerView.as_view(), name='broker_page'),

    path('consultas/extratos/', clients.ApplicationOpUserListView.as_view(),
         name='operationsstatement_page'),
    path('consultas/relatorio/', clients.ReportView.as_view(), name='report_page'),
    path('consultas/invetimentos/', clients.ProductPurcahseListView.as_view(),
         name='products_purchase_list'),
    path('consultas/invetimentos/editar/<int:pk>/',
         clients.ProductPurchaseUpdateView.as_view(), name='products_purchase_update'),
    path('consultas/contrato/<int:pk>/',
         clients.UserAgreementPrintView.as_view(), name='agreement_detail'),
    path('consultas/termos-de-aceite/',
         clients.UserAcceptanceTermListView.as_view(), name='acceptance_term_list'),
    path('consultas/termos-de-aceite/<int:pk>/',
         clients.UserAcceptanceTermPrintView.as_view(), name='acceptance_term_detail'),

    path('dashboard-data/', dashboards.ClientDashboardJson.as_view(),
         name='dashboard_client_data'),
    path('dashboard-products/', core_dash_views.ProductsDashboardJson.as_view(),
         name='dashboard_client_products_data'),

    path('trasferencias/aporte/<int:pk>/',
         operations.ClientDepositView.as_view(), name='deposit_create'),
    path('trasferencias/resgate/<int:pk>/',
         operations.ClientWithdrawView.as_view(), name='withdraw_create'),
    path('transferencias/',
         operations.MoneyTransferListView.as_view(), name='moneytransfer_list'),

    path('ajuda/', clients.HelpView.as_view(), name='help_page'),

]
