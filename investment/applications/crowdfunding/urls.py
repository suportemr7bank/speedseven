"""
Crowdfunding views
"""

from django.urls import path

from .views import ApplicationDepositListView

# pylint: disable=invalid-name
app_name = 'crowdfunding'

urlpatterns = [
    path('crowdfunding/depositos/<int:pk>',
         ApplicationDepositListView.as_view(), name='application_deposit_list'),
]
