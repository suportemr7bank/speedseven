
"""
    Accounts related view
"""
import logging
import pydoc

from allauth.utils import get_form_class
from allauth.account.views import LoginView as _LoginView
from allauth.account.views import SignupView as _SignupView
from allauth.account.utils import complete_signup
from allauth.account import app_settings

from allauth.exceptions import ImmediateHttpResponse
from django.conf import settings
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views import View

from accounts.invitations import Invitation
from accounts.auth import mixins as auth_mixins
from common.forms import mixins as filter_mixins
from common.messages import message_add
from common.views import generic, mixins


from . import forms, tables, invitations, models

logger = logging.getLogger(settings.DB_LOGGER)


class LoginView(auth_mixins.ConfigRequiredMixin, _LoginView):
    """
    Login view customization to include permission layer
    """
    config_required = {'ACCOUNT_ENABLE_SIGNIN': True}


class SignupView(auth_mixins.ConfigRequiredMixin, _SignupView):
    """
    Signup view customization to include permission layer
    Signup form can be set according to Role
    The form class loaded from Role.signup_form field

    """
    config_required = {'ACCOUNT_ENABLE_SIGNUP': True}
    acceptance_required = False
    __term = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.invitation = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['acceptance_required'] = self.acceptance_required
        context['term'] = self.__term
        return context

    def get_term(self):
        """
        Return {title: <title>, text: <text>} for term acceptance
        """
        return dict()

    def form_valid(self, form):
        # pylint: disable=attribute-defined-outside-init
        if self.acceptance_required and not self.__term:
            return self.form_invalid(form)

        self.user = form.save(self.request)
        try:
            return complete_signup(
                self.request,
                self.user,
                # pylint: disable=no-member
                app_settings.EMAIL_VERIFICATION,
                self.get_success_url(),
                signal_kwargs={
                    'form_data': form.cleaned_data
                }
            )
        except ImmediateHttpResponse as exc:
            return exc.response
        except ConnectionRefusedError as cre:
            self.user.delete()
            logger.exception(cre)
            return render(self.request, 'account/signup_unavailable.html')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if self.invitation:
            form.fields['email'].widget.attrs['readonly'] = True
        return form

    def get_form_class(self):
        self.__term = self.get_term()
        if self.invitation and self.invitation.role:
            # If invitation has role, get signup_form class from there, if it is not null
            form_class = self._signup_role_form(self.invitation.role)
            if form_class:
                return form_class
        else:
            signup_form = getattr(
                settings, 'ACCOUNTS_DEFAULT_SIGNUP_FORM', None)
            if signup_form:
                if form_class := pydoc.locate(signup_form):
                    return form_class

        # Defaul allauth signup form defined in settings
        # pylint: disable=no-member
        return get_form_class(app_settings.FORMS, "signup", self.form_class)

    def _signup_role_form(self, role):
        signup_forms = getattr(
            settings, 'ACCOUNTS_INVITATION_ROLE_SIGNUP_FORMS', None)
        if signup_forms:
            if form_path := signup_forms.get(role):
                form_class = pydoc.locate(form_path)
                return form_class
        return None

    def has_config_permissions(self):
        """
        Allow invitation signup even if signup is disabled
        """

        email = self.request.session.get('account_verified_email')
        if email:
            invitation = invitations.Invitation.objects.filter(
                email__iexact=email).last()
            if invitation and not invitation.key_expired():
                self.invitation = invitation
                return True

        return super().has_config_permissions()


class InvitationListView(mixins.AdminMixin,
                         filter_mixins.InvitationEmailFilterMixin,
                         mixins.ListViewMixin):
    """
        Admin list
    """
    config_required = {'ACCOUNT_ENABLE_INVITATION': True}
    permission_required = 'is_admin'
    model = Invitation
    table_class = tables.InvitationTable
    template_name = 'common/list.html'
    title = 'Convites'
    controls = [
        {'link': {'text': 'Novo', 'url': 'invitations:invitation_create'}},
    ]


class InvitationCreateView(mixins.AdminMixin,
                           invitations.CreateInivitationMixin,
                           generic.FormView):
    """
        Create admin
    """
    config_required = {'ACCOUNT_ENABLE_INVITATION': True}
    permission_required = 'is_admin'
    form_class = forms.InvitationForm
    template_name = 'common/form.html'
    title = 'Convites'
    success_url = reverse_lazy('invitations:invitation_list')
    cancel_url = success_url

    def get_controls(self):
        """
            Default form controls list
        """
        return [
            mixins.ControlFactory.cancel_button(
                reverse('invitations:invitation_list')),
            mixins.ControlFactory.button('send', 'Enviar', 'success'),
        ]


class InvitationUpdateView(mixins.AdminMixin,
                           invitations.SendInivitationMixin,
                           generic.UpdateView):
    """
        Update and Delete invitation
    """
    config_required = {'ACCOUNT_ENABLE_INVITATION': True}
    permission_required = 'is_admin'
    model = Invitation
    form_class = forms.InvitationForm
    template_name = 'common/form.html'
    title = 'Convites'
    success_url = reverse_lazy('invitations:invitation_list')
    cancel_url = success_url

    def form_valid(self, form):
        button = self.request.POST.get('button', None)
        if button == 'delete':
            self.object.delete()
            message_add(self.request, "Convite removido com sucesso")
            return HttpResponseRedirect(self.get_success_url())
        elif button == 'resend':
            invitation = self.object
            self.send_invitation(invitation)
            message_add(self.request, "Convite reinviado")
            return HttpResponseRedirect(self.get_success_url())
        # TODO: Padronizar http error
        return HttpResponseBadRequest('Requisição inválida')

    def get_controls(self):
        """
            Default form controls list
        """
        return [
            mixins.ControlFactory.cancel_button(
                reverse('invitations:invitation_list')),
            mixins.ControlFactory.delete_button(),
            mixins.ControlFactory.button('resend', 'Reenviar', 'success')
        ]


class ApiAcessListView(mixins.AdminMixin,
                       mixins.ListViewMixin):
    """
        Admin list
    """
    config_required = {'ACCOUNT_ENABLE_INVITATION': True}
    permission_required = 'is_admin'
    model = models.ApiAccess
    table_class = tables.ApiAccessTable
    template_name = 'common/list.html'
    title = 'Acesso à API'
    controls = [
        {'link': {'text': 'Novo acesso', 'url': 'accounts:api_access_create'}},
    ]


class ApiAccessCreateView(mixins.AdminMixin,
                          generic.CreateView):
    """
        Create admin
    """
    config_required = {'ACCOUNT_ENABLE_INVITATION': True}
    permission_required = 'is_admin'
    form_class = forms.ApiAccessForm
    template_name = 'common/form.html'
    title = 'Acesso à API'
    success_url = reverse_lazy('accounts:api_access_list')
    cancel_url = success_url

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class ApiAccessUpdateView(mixins.AdminMixin,
                          generic.UpdateView):
    """
        Create admin
    """
    config_required = {'ACCOUNT_ENABLE_INVITATION': True}
    permission_required = 'is_admin'
    model = models.ApiAccess
    form_class = forms.ApiAccessForm
    template_name = 'common/form.html'
    title = 'Acesso à API'
    success_url = reverse_lazy('accounts:api_access_list')
    cancel_url = success_url


class ThemeView(auth_mixins.LoginRequiredMixin, View):
    """
    User profile theme view
    """

    def post(self, request, *args, **kwargs):
        """
        Change user profile theme
        """
        if request.POST.get('theme'):
            theme = models.UserProfile.Theme.DARK
        else:
            theme = models.UserProfile.Theme.LIGHT

        user = request.user
        if profile := getattr(user, 'userprofile', None):
            profile.theme = theme
            profile.save()

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
