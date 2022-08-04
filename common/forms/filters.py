"""
    Forms to filter list/table rows
"""

from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Layout, Submit
from django import forms


class FilterFormBase(forms.Form):
    """
    Base form for filtering
    Just provides logged user attribute to form
    Used together FilterFormViewMixin
    """

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)


class NameEmailFilterForm(FilterFormBase):
    """
    Form to filter by name or email
    """

    field_name = forms.ChoiceField(label='',
                                   choices=[
                                       ('name', 'Nome'),
                                       ('email', 'Email')
                                   ],
                                   required=False)

    value = forms.CharField(max_length=512, label='', required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.form_class = 'col'
        self.helper.layout = Layout(
            Column('field_name', css_class='col-12 col-md-auto'),
            Column('value', css_class='col-12 col-md-auto'),
            Column(FormActions(Submit('', 'Filtrar', css_class='col-12 btn-success')),
                   css_class='col-12 col-md-auto')
        )


class EmailFilterForm(FilterFormBase):
    """
    Form to filter email
    """

    field_name = forms.ChoiceField(label='',
                                   choices=[
                                       ('email', 'Email')
                                   ],
                                   required=False)

    value = forms.CharField(max_length=512, label='', required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.form_class = 'row'
        self.helper.layout = Layout(
            Column('field_name', css_class='col-12 col-md-auto'),
            Column('value', css_class='col-12 col-md-auto'),
            Column(FormActions(Submit('', 'Filtrar', css_class='col-12  btn-success')),
                   css_class='col-12 col-md-auto')
        )
