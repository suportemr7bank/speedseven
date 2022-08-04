"""
Invitations urls
"""
from django.conf.urls import url
from django.urls import path

#django-invitations
from invitations import views as invitations_view
from . import views

#pylint: disable=invalid-name
#required for django-invitations to work properly (email url creation)
app_name = 'invitations'

urlpatterns = [
    # django-invitations url to accept-invite
    url(r'^aceitar-convite/(?P<key>\w+)/?$',
        invitations_view.AcceptInvite.as_view(), name='accept-invite'),

    path('', views.InvitationListView.as_view(), name='invitation_list'),
    path('novo/',
         views.InvitationCreateView.as_view(), name='invitation_create'),
    path('editar/<int:pk>/',
         views.InvitationUpdateView.as_view(), name='invitation_update'),
]
