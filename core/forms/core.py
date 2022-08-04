"""
    Forms customization
"""
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Layout, Row, Field, HTML
from django import forms
from django.contrib.sites.models import Site

from .. import models


class UserActivationForm(forms.ModelForm):
    """
    Change User form requirements
    """
    class Meta:
        """
            Meta configuration
        """
        model = models.User
        fields = ['first_name', 'last_name', 'email', 'is_active']

    def __init__(self, *args, **kwargs) -> None:
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['first_name'].disabled = True
        self.fields['last_name'].disabled = True
        self.fields['email'].disabled = True


class AdminForm(forms.ModelForm):
    """
    Set user as admin
    """

    class Meta:
        """
        Meta configuration
        """
        model = models.User
        fields = ['first_name', 'last_name', 'email', 'is_active']

    def __init__(self, *args, **kwargs) -> None:
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True
        if self.instance.pk:
            if self.instance.pk == self.user.pk:
                self.fields.pop('is_active')

    def clean(self):
        """
            Prevent duplicated email
        """
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        if 'email' in self.changed_data:
            if models.User.objects.filter(email__iexact=email).exists():
                self.add_error('email', "Um usuário com este email já existe")
        return cleaned_data

    def save(self, commit=True):
        """
            Save email in the username field
        """
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class AccepanceTermForm(forms.ModelForm):
    """
    Acceptance term form
    """

    class Meta:
        """
        Meta class
        """
        model = models.AcceptanceTerm
        fields = ['title', 'type', 'version',
                  'is_active', 'annotation', 'text']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

        self.helper.layout = Layout(
            Row(
                Column(
                    Row('title'),
                    Row(Column('type'), Column('version'), Column(
                        'is_active', css_class='mt-4 pt-3'))
                ),
                Column(Field('annotation', rows=5))
            ),
            Row(Column(Field('text', rows=20))),
        )


class CompanyForm(forms.ModelForm):
    """
    Company form
    """

    class Meta:
        """
        Meta class
        """
        model = models.Company
        fields = ['name', 'cnpj', 'bank_name', 'bank_code', 'bank_ispb',
                  'bank_branch_number', 'bank_branch_digit', 'account_number', 'account_digit']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(Column('name'), Column('cnpj'), Column(HTML(''))),
            Row(HTML('<hr>'), css_class='my-2'),
            Row(Column('bank_name'), Column(''), Column(HTML(''))),
            Row(Column('bank_code'), Column('bank_ispb'), Column(HTML(''))),
            Row(Column('bank_branch_number'), Column(
                'bank_branch_digit'), Column(HTML(''))),
            Row(Column('account_number'), Column(
                'account_digit'), Column(HTML('')))
        )
