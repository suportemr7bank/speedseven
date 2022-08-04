
"""
     Urls
"""
from django.urls import path
from . import views

# pylint: disable=invalid-name
app_name = 'emailtemplate'

urlpatterns = [
    path('modelo-de-email/', views.EmailTemplateListView.as_view(), name='emailtemplate_list'),
    path('modelo-de-email/novo/',
         views.EmailTemplateCreateView.as_view(), name='emailtemplate_create'),
    path('modelo-de-email/editar/<int:pk>/',
         views.EmailTemplateUpdateView.as_view(), name='emailtemplate_update'),

]
