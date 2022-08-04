"""
Accounts and invitations urls

"""
import pydoc
from allauth.account import views as allauth_views
from django.urls import path, re_path
from django.conf import settings

from . import views

signup_class_path = getattr(settings, "ACCOUNTS_SIGNUP_VIEW", None)
if signup_class_path:
    signup_view = pydoc.locate(signup_class_path)
else:
    signup_view = views.SignupView

#pylint: disable=line-too-long
urlpatterns = [

    path("login/", views.LoginView.as_view(), name="account_login"),
    path("logout/", allauth_views.logout, name="account_logout"),
    path("signup/", signup_view.as_view(), name="account_signup"),

    path("password/set/", allauth_views.password_set,
         name="account_set_password"),
    path("password/change/", allauth_views.password_change,
         name="account_change_password"),
    path("password/reset/", allauth_views.password_reset,
         name="account_reset_password"),
    path("password/reset/done/", allauth_views.password_reset_done,
         name="account_reset_password_done"),
    path("password/reset/key/done/", allauth_views.password_reset_from_key_done,
         name="account_reset_password_from_key_done"),
    re_path(r"^password/reset/key/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>.+)/$",
            allauth_views.password_reset_from_key, name="account_reset_password_from_key"),

    path("email/", allauth_views.email, name="account_email"),
    path("confirm-email/", allauth_views.email_verification_sent,
         name="account_email_verification_sent"),
    re_path(r"^confirm-email/(?P<key>[-:\w]+)/$",
            allauth_views.confirm_email, name="account_confirm_email"),

    # TODO: tratar conta inativa
    path("inactive/", allauth_views.account_inactive, name="account_inactive"),

    path("perfil/tema/", views.ThemeView.as_view(), name="account_profile_theme"),

]
