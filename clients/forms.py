"""
Cliens forms
"""

from crispy_forms.bootstrap import InlineRadios
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Column, Field, Layout, Row, HTML
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import SetPasswordForm
from django.db import IntegrityError, transaction

from accounts import roles as account_roles
from accounts import models as accounts_models
from accounts.forms import SignupForm as _SignupForm
from clients.models import Client
from common.forms import fields
from core import models as core_models
from core import workflow

from . import models


class ClientFormBase(forms.ModelForm):
    """
    Client form common methods
    """

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.operator = kwargs.pop('operator', None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout()

    def clean(self):
        cleaned_data = super().clean()
        if not self.instance.pk and cleaned_data.get('email', None):
            user_model = get_user_model()
            if user_model.objects.filter(email=cleaned_data['email'], is_active=True).exists():
                self.add_error(
                    'email', 'Já existe um usuário ativo com este email')
        return cleaned_data

    def save(self, commit=True):
        """
        Insert logged user to client
        """
        client = super().save(commit=False)
        client.operator = self.operator
        if commit:
            try:
                with transaction.atomic():
                    if not getattr(client, 'user', None):
                        if self.user:
                            user = self.user
                        else:
                            user = self._create_user()
                            models.Client.set_role_and_email(user)
                        client.user = user
                    else:
                        user = client.user
                        user.first_name = self.cleaned_data['first_name']
                        user.last_name = self.cleaned_data['last_name']
                        user.save()
                    client.save()
            except IntegrityError as exc:
                raise exc
        return client

    def _create_user(self):
        user_model = get_user_model()
        user = user_model.objects.create(
            username=self.cleaned_data['email'],
            email=self.cleaned_data['email'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name']
        )
        if not getattr(user, 'userprofile', None):
            #pylint: disable=no-member
            accounts_models.UserProfile.objects.create(user=user)
        return user


class ClientForm(workflow.ApprovalWorkflowFormMixin, ClientFormBase):
    """
    Create a client and inser the logged user
    """

    email = forms.EmailField(label='Email')

    class Meta:
        """
        Meta class
        """
        model = models.Client
        exclude = ['user']
        widgets = {
            'type': forms.widgets.RadioSelect,
            'birth_date': fields.DatePickerInput(options={'dateFormat': 'd/m/Y'}),
            'message': forms.widgets.Textarea(attrs={'rows': 4})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        client_type = None
        if self.instance.pk:
            client_type = self.instance.type
            self.fields.pop('type', None)
            self.fields.pop('email', None)
        self._set_required_fields(client_type)
        self._select_layout()

    def _set_required_fields(self, client_type):
        if self.user:
            required_fields = models.Client.required_fields(client_type)
            for key in required_fields:
                self.fields[key].required = True

    def _select_layout(self):
        if self.instance.pk:
            if self.instance.type == models.Client.Type.PF:
                self.fields.pop('cnpj')
                self.fields.pop('company_name')
                self._set_pf_layout(self.helper)
            elif self.instance.type == models.Client.Type.PJ:
                self._set_pj_layout(self.helper)

        else:
            self.fields['type'].label = ""
            # enabled by javascript according to type field
            self.fields['cnpj'].disabled = True
            self.fields['company_name'].disabled = True
            self.fields['company_agreement'].disabled = True
            self._set_layout(self.helper)

    def _set_pf_layout(self, helper):
        helper.layout = Layout(self.workflow_layout,
                               Row(Column('politically_exposed', css_class='my-2'),
                                   Column(HTML('')), Column(HTML(''))),
                               Row(Column('first_name'), Column(
                                   'last_name'), Column(HTML(''))),
                               Row(Column(Field('phone', css_class='phone')), Column(
                                   Field('cpf', css_class='cpf')), Column(Field('birth_date', css_class='date'))),
                               Row(Column(Field('zip_code', css_class='zip_code')),
                                   Column('city'), Column('state')),
                               Row(Column('address'), Column(
                                   'number'), Column('complement')),
                               Row(Column('rg_cnh'), Column(
                                   'address_proof'), Column(HTML(''))),
                               )

    def _set_pj_layout(self, helper):
        helper.layout = Layout(self.workflow_layout,
                               Row(Column('politically_exposed', css_class='my-2'),
                                   Column(HTML('')), Column(HTML(''))),
                               Row(Column('first_name'), Column('last_name'),
                                   Column(Field('cpf', css_class='cpf'))),
                               Row(Column(Field('birth_date', css_class='date')),
                                   Column('rg_cnh'), Column('address_proof')),
                               Row(HTML(
                                   '<p class="h4 mt-4 mb-4 text-secondary"> Dados da empresa </p>')),
                               Row(Column('company_name'), Column(
                                   Field('phone', css_class='phone')), Column(HTML(''))),
                               Row(Column(Field('cnpj', css_class='cnpj')),
                                   Column('company_agreement'), Column(HTML(''))),
                               Row(Column(Field('zip_code', css_class='zip_code')),
                                   Column('city'), Column('state')),
                               Row(Column('address'), Column(
                                   'number'), Column('complement')),
                               )

    def _set_layout(self, helper):
        helper.layout = Layout(
            Row(Column(HTML('<p class="h6 pt-2 text-secondary">Atenção! Clientes cadastrados aqui não receberão convites ou email de confirmação</p>'))),
            Row(Column(HTML('<p class="h6 pb-3 text-secondary">Para alterar/criar a senha do cliente, acesse o menu Usuários > Ativação e senha</p>'))),
            Row(Column(InlineRadios('type')),
                Column(HTML('')), Column(HTML(''))),
            Row(Column('politically_exposed', css_class='my-2'),
                Column(HTML('')), Column(HTML(''))),
            Row(Column('email'), Column('first_name'), Column('last_name')),
            Row(Column(Field('cpf', css_class='cpf')), Column(
                Field('birth_date', css_class='date')), Column(HTML(''))),
            Row(Column(Field('phone', css_class='phone')),
                Column('rg_cnh'), Column('address_proof')),
            Row(HTML('<hr class="my-4">')),
            Row(Column('company_name'), Column(
                Field('cnpj', css_class='cnpj')), Column('company_agreement')),
            Row(Column(Field('zip_code', css_class='zip_code')),
                Column('city'), Column('state')),
            Row(Column('address'), Column('number'), Column('complement')),
        )


class Password(SetPasswordForm):
    """
    Password form adapter
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(self.user, *args, **kwargs)


class ClientCreateForm(ClientFormBase, Password):
    """
    Create a client and inser the logged user
    """

    NEXT_STEP_INSERT = 'INS'
    NEXT_STEP_CLIENT = 'CLI'

    email = forms.EmailField(label='Email')
    next_step = forms.ChoiceField(
        label='Próxima etapa',
        choices=[('', '-----'), ('INS', 'Inserir dados do cliente'),
                 ('CLI', 'Deixar cliente inserir dados')],
        required=True
    )

    class Meta:
        """
        Meta class
        """
        model = models.Client
        fields = ['type', 'email', 'first_name', 'last_name', 'next_step']
        widgets = {
            'type': forms.widgets.RadioSelect,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._set_layout()

    def clean(self):
        self.clean_new_password2()
        return super().clean()

    def _set_layout(self):
        self.helper.layout = Layout(
            Row(Column(HTML('<p class="h6 pt-2 text-secondary">Atenção! Clientes cadastrados aqui não receberão convites ou email de confirmação</p>'))),
            Row(Column(HTML('<p class="h6 pb-4 text-secondary">Os dados do cliente poderão ser preenchidos acessando o registro do cliente</p>'))),
            Row(Column(InlineRadios('type')),
                Column(HTML('')), Column(HTML(''))),
            Row(Column('email'), Column(HTML('')), Column(HTML(''))),
            Row(Column('first_name'), Column('last_name'), Column(HTML(''))),
            Row(Column('new_password1'), Column(
                'new_password2'), Column(HTML(''))),
            Row(Column('next_step'), Column(HTML('')), Column(HTML(''))),
        )

    def save(self, commit=True):
        obj = super(ClientCreateForm, self).save(commit)
        self.user = obj.user
        super(Password, self).save(commit)
        return obj


class SignupForm(_SignupForm):
    """
    Signup form customization for clients
    Requires extra client data and a acceptance term
    """

    account_type = forms.ChoiceField(
        choices=Client.Type.choices,
        label=""
    )

    first_name = forms.CharField(max_length=150, label='',
                                 widget=forms.TextInput(
                                     attrs={"placeholder": 'Nome*'}
                                 ), required=True)

    last_name = forms.CharField(max_length=150, label='',
                                widget=forms.TextInput(
                                    attrs={"placeholder": "Sobrenome*"}
                                ), required=True)

    cpf = forms.CharField(max_length=14, label='',  widget=forms.TextInput(
        attrs={"placeholder": "CPF", 'class': 'cpf'}
    ), required=True)

    accept_terms = forms.BooleanField(
        initial=False, widget=forms.HiddenInput())

    field_order = ['account_type', 'cpf']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(Column('account_type')),
            Row(Column('first_name'), Column('last_name')),
            Row(Column('email'), Column('cpf')),
            Row(Column('password1'), Column('password2')),
            'accept_terms'
        )

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('accept_terms', False):
            self.add_error('', 'É necessário aceitar o termo para continuar')
        return cleaned_data

    def save(self, request):
        user = super().save(request)
        user.username = user.email
        user.save()
        user_role = account_roles.get_last_user_role(user)
        user_role.role = account_roles.Roles.CLIENT
        user_role.save()
        return user


class UserAcceptanceTermForm(forms.Form):
    """
    Form te accept and save term
    """

    accept_term = forms.BooleanField(
        initial=False, label='Li e aceito os termos', required=False)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.term = kwargs.pop('term', None)
        super().__init__(*args, **kwargs)

        self._set_layout()

    def _set_layout(self):
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('accept_term')
        )

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('accept_term', None):
            self.add_error(
                'accept_term', 'Para continuar é preciso aceitar os termos')
        if self.term is None:
            self.add_error('accept_term', 'Termo de aceite não encontrado')
        if self.user is None:
            self.add_error('accept_term', 'Usuário não encontrado')

    def save(self, commit=True):
        """
        Create a user acceptance term
        """
        obj = None
        if commit:
            # pylint: disable=no-member
            obj = core_models.UserAcceptanceTerm.objects.create(
                user=self.user,
                term=self.term
            )
        return obj
