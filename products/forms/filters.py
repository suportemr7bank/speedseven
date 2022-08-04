"""
    Forms to filter list/table rows
"""

from crispy_forms.bootstrap import FormActions, PrependedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Layout, Submit

from django import forms
from django.utils import timezone

from common.forms import fields
from common.forms import filters
from investment import models as invest_models

from ..models import Product


class OperationsFilterForm(filters.FilterFormBase):
    """
    Form to filter client operations in report
    """

    period_time_days = 60

    product = forms.ChoiceField(
        label='', choices=[('', 'Produto')], required=False)
    operation = forms.ChoiceField(
        label='', choices=[('', 'Operação')], required=False)

    init_date = forms.DateField(
        label='',
        required=False,
        widget=fields.DatePickerInput(options={'dateFormat': 'd/m/Y'}),
    )

    final_date = forms.DateField(
        label='',
        required=False,
        widget=fields.DatePickerInput(options={'dateFormat': 'd/m/Y'}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].choices += Product.objects.filter(
            application__is_active=True,
            application__applicationaccount__user=self.user,
        ).values_list('pk', 'display_text')
        self.fields['operation'].choices += invest_models.ApplicationOp.OperationType.choices

        if not self.data:
            current_date = timezone.localdate(timezone.now())
            init_date = current_date - \
                timezone.timedelta(days=self.period_time_days)
            self.fields['init_date'].initial = init_date
            self.fields['final_date'].initial = current_date

        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.form_class = 'row'
        self.helper.layout = Layout(
            Column('product', css_class='col-12 col-md-auto'),
            Column('operation', css_class='col-12 col-md-auto'),
            Column(PrependedText('init_date', 'Início'),
                   css_class='col-12 col-md-auto'),
            Column(PrependedText('final_date', 'Fim'),
                   css_class='col-12 col-md-auto'),
            Column(FormActions(Submit('', 'Filtrar', css_class='col-12 btn-success')),
                   css_class='col-12 col-md-auto')
        )
