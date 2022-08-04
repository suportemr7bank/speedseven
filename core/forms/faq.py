"""
FAQ form
"""

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row
from django import forms
from core import models


class FAQForm(forms.ModelForm):
    """
    Acceptance term form
    """

    class Meta:
        """
        Meta class
        """
        model = models.FAQ
        fields = '__all__'
        widgets = {
            'faq_config': forms.widgets.CheckboxSelectMultiple
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.instance.pk:
            #pylint: disable=no-member
            try:
                last_question_order = models.FAQ.objects.latest('order')
                self.initial['order'] = last_question_order.order + 1
            except models.FAQ.DoesNotExist:
                self.initial['order'] = 1

        self.helper = FormHelper()

        self.helper.layout = Layout(
            Row('question'),
            Row('answer'),
            Row('order'),
            Row('faq_config'),
        )
