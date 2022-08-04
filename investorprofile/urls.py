
"""
     Urls
"""
from django.urls import path

from . import views

# pylint: disable=invalid-name
app_name = 'investorprofile'

urlpatterns = [
    path('teste-de-perfil/', views.ProfileTestListView.as_view(),
         name='profile_test_list'),

    path('teste-de-perfil/editar/<int:pk>/',
         views.ProfileTestUpdateView.as_view(), name='profile_test_update'),

    path('teste-de-perfil/preview/<int:pk>/', views.ProfileTestDetailView.as_view(),
         name='profile_test_detail'),

]
