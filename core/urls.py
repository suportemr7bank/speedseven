
"""
     Urls
"""
from django.urls import path
from .views import accept_terms, core, email, bank, faq, site

# pylint: disable=invalid-name
app_name = 'core'

urlpatterns = [
    path('inicio/', core.StartView.as_view(), name='start_page'),

    path('usuarios/administradores/',
         core.AdminListView.as_view(), name='admin_list'),
    path('usuarios/administradores/editar/<int:pk>/',
         core.AdminUpdateView.as_view(), name='admin_update'),
    path('usuarios/administradores/alterar-senha/<int:pk>/',
         core.ChangeAdminPasswordView.as_view(), name='change_admin_password'),

    path('usuarios/ativacao-senha/', core.UserListView.as_view(), name='user_list'),
    path('usuarios/ativacao-senha/editar/<int:pk>/',
         core.UserUpdateView.as_view(), name='user_update'),
    path('usuarios/ativacao-senha/alterar-senha/<int:pk>/',
         core.ChangeUserPasswordView.as_view(), name='change_user_password'),

    path('usuarios/clientes/', core.ClientListView.as_view(), name='client_list'),
    path('usuarios/clientes/novo/',
         core.ClientCreateView.as_view(), name='client_create'),
    path('usuarios/clientes/editar/<int:pk>/',
         core.ClientUpdateView.as_view(), name='client_update'),

    path('usuarios/mensagens/', email.EmailListView.as_view(), name='email_list'),
    path('usuarios/mensagens/novo/',
         email.EmailCreateView.as_view(), name='email_create'),
    path('usuarios/mensagens/detalhe/<int:pk>/',
         email.EmailUpdateView.as_view(), name='email_detail'),
    path('usuarios/mensagens/log/<int:pk>/',
         email.EmailLogView.as_view(), name='email_log'),

    path('usuarios/dados-bancarios/',
         bank.BankAccountListView.as_view(), name='bank_account_list'),
    path('usuarios/dados-bancarios/novo/',
         bank.BankAccountCreateView.as_view(), name='bank_account_create'),
    path('usuarios/dados-bancarios/editar/<int:pk>/',
         bank.BankAccountUpdateView.as_view(), name='bank_account_update'),


    path('contratos/termos-de-aceite/', accept_terms.AcceptanceTermListView.as_view(),
         name='acceptance_term_list'),
    path('contratos/termos-de-aceite/novo/',
         accept_terms.AcceptanceTermCreateView.as_view(), name='acceptance_term_create'),
    path('contratos/termos-de-aceite/editar/<int:pk>/',
         accept_terms.AcceptanceTermUpdateView.as_view(), name='acceptance_term_update'),

    path('api/', core.ApiUserView.as_view(), name='api_page'),

    path('tarefas/', core.WorkflowTaskListView.as_view(), name='task_list'),

    path('configuracoes/empresa/',
         core.CompanyListView.as_view(), name='company_list'),
    path('configuracoes/empresa/novo/',
         core.CompanyCreateView.as_view(), name='company_create'),
    path('configuracoes/empresa/editar/<int:pk>/',
         core.CompanyUpdateView.as_view(), name='company_update'),

    path('configurações/faq/',
         faq.FAQConfigListView.as_view(), name='faq_config_list'),
    path('configurações/faq/novo/',
         faq.FAQConfigCreateView.as_view(), name='faq_config_create'),
    path('configurações/faq/editar/<int:pk>/',
         faq.FAQConfigUpdateView.as_view(), name='faq_config_update'),

    path('configurações/faq/questoes/',
         faq.FAQListView.as_view(), name='faq_list'),
    path('configurações/faq/questoes/novo/',
         faq.FAQCreateView.as_view(), name='faq_create'),
    path('configurações/faq/questoes/editar/<int:pk>/',
         faq.FAQUpdateView.as_view(), name='faq_update'),

    path('configuracoes/pagina-inicial/',
         site.StartPageListView.as_view(), name='start_page_list'),
    path('configuracoes/pagina-inicial/novo/',
         site.StartPageCreateView.as_view(), name='start_page_create'),
    path('configuracoes/pagina-inicial/editar/<int:pk>/',
         site.StartPageUpdateView.as_view(), name='start_page_update'),

]
