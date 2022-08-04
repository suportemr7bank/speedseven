"""
Formatters
"""

from decimal import Decimal
from django.utils.formats import localize


def decimal_format(value, places=2):
    """ Two dedimal places number formatting """
    if places >= 1:
        return localize(Decimal(value).quantize(Decimal(f'0.{"0"*(places-1)}1')), use_l10n=True)
    else:
        return value


class DecimalFieldFormMixin:
    """
    Money field default
    """
    decimal_fields = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, digits in self.decimal_fields.items():
            self.fields[field_name].widget.attrs['class'] = 'decimal-input'
            self.fields[field_name].widget.attrs['data-digits'] = f'{digits}'
            self.fields[field_name].localize = True
            self.fields[field_name].widget.is_localized = True
            self.fields[field_name].widget.input_type = 'text'
            if getattr(self, 'instance', None):
                if getattr(self.instance, field_name):
                    self.initial[field_name] = decimal_format(self.initial[field_name], digits)
