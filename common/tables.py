"""
Common tables
"""

from decimal import Decimal
import django_tables2


class MoneyColumn(django_tables2.Column):
    """
    Number column
    Two decima places with comma separtor
    """
    attrs={
            "td": {"align": "right"},
        }

    def render(self, value):
        return Decimal(value).quantize(Decimal('0.01'))


class PercentColumn(django_tables2.Column):
    """
    Number column
    Two decima places with comma separtor
    """
    attrs={
            "td": {"align": "right"},
        }

    def render(self, value):
        return Decimal(value).quantize(Decimal('0.01'))