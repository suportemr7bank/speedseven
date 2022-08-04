"""
    Forms customization
"""
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from django import forms
from django.contrib.auth import get_user_model
from accounts.models import Roles

from core import models


class EmailBatchForm(forms.ModelForm):
    """
    Send generic batch email
    """

    class Meta:
        """
        Meta class
        """
        model = models.EmailBatchMessage
        fields = ['role', 'subject', 'message']

    def __init__(self, *args, **kwargs) -> None:
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['role'].label = 'Enviar para'

        choices = self.fields['role'].choices
        choices.remove((Roles.UNDEF.value, Roles.UNDEF.label))
        self.fields['role'].choices = choices

        self.helper = FormHelper()

        self.helper.layout = Layout(
            'role',
            'subject',
            'message'
        )

    def save(self, commit=True):
        obj = super().save(commit=False)
        user_model = get_user_model()
        users = user_model.objects.filter(is_active=True, userrole__role=obj.role)
        obj.sender = self.user
        obj.total = users.count()
        if commit:
            obj.save()
        return obj
