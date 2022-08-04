"""
Form helpers

"""

from crispy_forms.helper import FormHelper


class FormSetHelper(FormHelper):
    """
    Helper class to hender formsets
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_tag = False
        self.render_required_fields = True
        self.template = 'bootstrap5/table_inline_formset.html'
