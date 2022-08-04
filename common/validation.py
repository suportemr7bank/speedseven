"""
Validation methods
"""

from django.core.exceptions import ValidationError


def validate_not_zero(value):
    """Validation function"""
    if value == 0:
        raise ValidationError(
            'Valor deve ser diferente de zero',
            params={'value': value},
        )


def validate_greater_than_zero(value):
    """Validation function"""
    if value <= 0:
        raise ValidationError(
            'Valor deve ser maior que zero',
            params={'value': value},
        )
