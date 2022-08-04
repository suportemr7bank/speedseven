"""
Forms customization
"""

from allauth.account.forms import LoginForm as _LoginForm
from allauth.account.forms import SignupForm as _SignupForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout

from django import forms
from django.contrib.auth import get_user_model

from accounts import models
from accounts import roles as account_roles

from .invitations import Invitation


class SignupForm(_SignupForm):
    """
    Remove username from form
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._init_default()

    def _init_default(self):
        self.fields.pop('username')
        self.fields['email'].label = ''
        self.fields['email'].widget.attrs.update(
            {'placeholder': "Endereço de email*"})
        self.fields['password1'].label = ''
        self.fields['password2'].label = ''

    def save(self, request):
        user = super().save(request)
        user.username = user.email
        user.save()
        account_roles.create_user_role_from_invitation(user)
        return user


class LoginForm(_LoginForm):
    """
    Remove username from form
    """

    def __init__(self, *args, **kwargs):
        self.error_messages["username_password_mismatch"] = "Usuário ou senha incorretos"
        self.error_messages["email_password_mismatch"] = "Email ou senha incorretos"
        super().__init__(*args, **kwargs)
        self.fields['login'].label = ''
        self.fields['password'].label = ''
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'login',
            'password'
        )


class InvitationForm(forms.ModelForm):
    """
    Invitation form customization. Only to get data. Do not handle saving.
    -Send email in background
    -Only admin as inviter
    """

    class Meta:
        """
        Meta class
        """
        model = Invitation
        fields = ['email', 'role']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Removing undefined (APIACC and UNDEF) role
        choices = list(account_roles.Roles.choices)
        choices.pop()
        choices.pop()
        self.fields['role'].choices = choices

    def clean(self):
        cleaned_data = super().clean()
        # instace existis only for update
        if not self.instance:
            if Invitation.objects.filter(email=cleaned_data['email']).exists():
                self.add_error('email', 'Já exite um convite para este email')
        return cleaned_data


class ApiAccessForm(forms.ModelForm):
    """
    Api access form
    """

    user_model = get_user_model()

    username = forms.CharField(label='Usuário')
    is_active = forms.BooleanField(label='Ativo', required=False)

    class Meta:
        """
        Meta class
        """
        model = models.ApiAccess
        fields = ['username', 'access_key', 'is_active']

    def __init__(self, *args, **kwargs):
        self.operator = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.instance.pk:
            self.initial['username'] = self.instance.user.username
            self.initial['is_active'] = self.instance.user.is_active

    def clean(self):
        """
        Prevent duplicated username
        """
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        if 'username' in self.changed_data:
            if self.user_model.objects.filter(username__iexact=username).exists():
                self.add_error(
                    'username', "Um usuário com este username já existe")
        return cleaned_data

    def save(self, commit=True):
        """
        Save user and this object
        """
        api_access = super().save(commit=False)

        if not getattr(self.instance, 'user', None):
            user = self.user_model.objects.create(
                username=self.cleaned_data['username'])
            user.is_active = self.cleaned_data['is_active']
            user.set_password(self.cleaned_data['access_key'])
            user.save()
            account_roles.create_user_role(user=user, role=account_roles.Roles.APIAPP)
            api_access.user = user
        else:
            user = self.instance.user
            user.username = self.cleaned_data['username']
            user.is_active = self.cleaned_data['is_active']
            if 'access_key' in self.changed_data:
                user.set_password(self.cleaned_data['access_key'])
            user.save()

        if not self.instance.pk:
            api_access.operator = self.operator

        api_access.save()

        return api_access
