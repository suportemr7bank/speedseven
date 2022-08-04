"""
Customize django flatpicker
"""

from django import forms
from django_select2 import forms as s2forms
from flatpickr import DatePickerInput as _DatePickerInput
from flatpickr import DateTimePickerInput as _DateTimePickerInput


class DatePickerInput(_DatePickerInput):
    """
    Prevend default cript loading in form rendering
    The scrips are loaded in main.js
    """

    @property
    def media(self):
        """
        Prevent media render
        """
        return forms.Media()


class DateTimePickerInput(_DateTimePickerInput):
    """
    Prevend default cript loading in form rendering
    The scrips are loaded in main.js
    """

    @property
    def media(self):
        """
        Prevent media render
        """
        return forms.Media()


class Select2Widget(s2forms.ModelSelect2Widget):
    """
    Select2Widget base
    """

    @property
    def media(self):
        """
        Customize select2 and load scripts
        """
    # pylint: disable=protected-access

        media = super().media

        return forms.Media(
            js=["https://code.jquery.com/jquery-3.6.0.min.js"] + media._js,
            css=media._css
        )


class UserWidget(Select2Widget):
    """
    Widget for django_select2
    """
    search_fields = [
        "email__icontains",
        "first_name__icontains",
        "last_name__icontains",
    ]
