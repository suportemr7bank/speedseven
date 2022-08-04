from django.urls import path
from . import views

app_name = 'website'

urlpatterns = [
    path('', views.LandingView.as_view(), name='landing_page'),
    path('produtos/', views.ProductsView.as_view(), name='product_page'),
    path('produtos/categorias/documentos/<int:pk>/',
         views.CategoryDocumentDetailView.as_view(), name='category_document_detail'),
    path('termos/<slug:type>/',
         views.AcceptanceTermPrintView.as_view(), name='term_page'),

]
