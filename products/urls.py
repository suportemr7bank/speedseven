
"""
     Urls
"""
from django.urls import path

from .views import agreements, products

# pylint: disable=invalid-name
app_name = 'products'

urlpatterns = [

    path('contratos/produtos/', agreements.AgreementListView.as_view(),
         name='agreement_list'),
    path('contratos/produtos/novo/',
         agreements.AgreementCreateView.as_view(), name='agreement_create'),
    path('contratos/produtos/editar/<int:pk>/',
         agreements.AgreementUpdateView.as_view(), name='agreement_update'),
    path('contratos/produtos/dados/',
         agreements.AgreementJsonView.as_view(), name='agreement_data'),
    path('contrato/preview/<int:pk>/',
         agreements.UserAgreementPreview.as_view(), name='agreement_preview'),
    path('contrato-cliente/<int:pk>/',
         agreements.UserAgreementPrintView.as_view(), name='agreement_detail'),

    path('produtos/', products.ProductListView.as_view(), name='product_list'),
    path('produtos/novo/',
         products.ProductCreateView.as_view(), name='product_create'),
    path('produtos/editar/<int:pk>/',
         products.ProductUpdateView.as_view(), name='product_update'),
    path('produto-info/', products.ProductJsonData.as_view(), name='product_info_js'),
    path('produtos-contratados/', products.ProductPurchaseListView.as_view(),
         name='product_purchase_list'),

    path('produtos/categorias/',
         products.ProductCategoryListView.as_view(), name='category_list'),
    path('produtos/categorias/novo/',
         products.ProductCategoryCreateView.as_view(), name='category_create'),
    path('produtos/categorias/editar/<int:pk>/',
         products.ProductCategoryUpdateView.as_view(), name='category_update'),

    path('produtos/categorias/documentos/',
         products.CategoryDocumentListView.as_view(), name='category_document_list'),
    path('produtos/categorias/documento/novo/',
         products.CategoryDocumentCreateView.as_view(), name='category_document_create'),
    path('produtos/categorias/documentos/editar/<int:pk>/',
         products.CategoryDocumentUpdateView.as_view(), name='category_document_update'),

    path('dashboads/', products.DashboardListView.as_view(),
         name='dashboard_list'),
    path('dashboads/novo/',
         products.DashboardCreateView.as_view(), name='dashboard_create'),
    path('dashboads/editar/<int:pk>/',
         products.DashboardUpdateView.as_view(), name='dashboard_update'),

    path('perfis/', products.ProfileProductListView.as_view(),
         name='profile_product_list'),
    path('perfis/novo/', products.ProfileProductCreate.as_view(),
         name='profile_product_create'),
    path('perfis/<int:pk>/', products.ProfileProductUpdate.as_view(),
         name='profile_product_update'),

]
