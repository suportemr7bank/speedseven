"""
Client api urls
"""

from django.urls import path
from . import views

urlpatterns = [
    path('client/', views.ClientCreateView.as_view()),
    path('client/<int:pk>/', views.ClientRetrieveUpdateView.as_view()),
]
