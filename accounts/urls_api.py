"""
Accounts and invitations urls
"""

from django.urls import path


from . import views

# pylint: disable=invalid-name
app_name = 'accounts'

urlpatterns = [
    path("acessos/", views.ApiAcessListView.as_view(),
         name="api_access_list"),
    path("acessos/novo/", views.ApiAccessCreateView.as_view(),
         name="api_access_create"),
    path("acessos/editar/<int:pk>/",
         views.ApiAccessUpdateView.as_view(), name="api_access_update"),
]
