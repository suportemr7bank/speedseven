"""
Generic validators
"""


from django.core.exceptions import ValidationError

def validate_greate_than_zero(value):
    """
    Values must be greater than zero
    """
    if value <= 0:
        raise ValidationError("Valor deve ser maior que zero")


def validate_null_or_greate_than_zero(value):
    """
    Values must be greater than zero or None
    """
    if value is not None and value <= 0:
        raise ValidationError("Valor deve ser maior ou igual a zero")


def validate_percentage_between_0_100(value):
    """
    Values must be between zero and one hundred (0, 100)
    """
    if value is None or value <= 0 or value >= 100:
        raise ValidationError("O valor deve estar entre 0 e 100")
