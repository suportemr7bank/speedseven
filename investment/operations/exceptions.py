"""
Operation exceptions
"""

from django.core.exceptions import ValidationError


class InvalidApplicationError(ValidationError):
    """ Application is not valid """


class InactiveApplicationError(ValidationError):
    """ Application is not active """


class SameOperationDateError(ValidationError):
    """ There is an operation with same date """


class DepositValueError(ValidationError):
    """ Invalid deposit value (value <= 0)"""


class WithdrawValueError(ValidationError):
    """ Invalid withdraw value (value <= 0)"""


class WithdrawNotEnoughBalanceError(ValidationError):
    """ Not enough balace to execute the operaiont (balance < value) """


class ReatroactiveOperationDateError(ValidationError):
    """
    Retroactive operation date is not allowed.
    Any operation modifies the balance based on the last operation made.
    If a retrospective operation is made, all next operations would be changed
    to ensure balance consistency.
    """
