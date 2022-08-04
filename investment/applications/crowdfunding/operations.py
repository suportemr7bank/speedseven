"""
Application operations
"""

from django.utils import timezone
from investment.interfaces.operations import AbstractAccountOperation
from investment.operations.exceptions import DepositValueError


def get_operation_date():
    """ The current date for operations"""
    return timezone.localtime(timezone.now())


class ApplicationAccountOperation(AbstractAccountOperation):
    """
    Warning!!!
    Operations must be validated before creating a deposit or withdraw
    """

    def make_deposit(self, operator, application_account, value,
                     description=None, operation_date=None):
        """
        Make a deposit
        """
        app_deposit = application_account.applicationdeposit
        app_deposit.date_completed = get_operation_date()
        app_deposit.save()
        return application_account.applicationdeposit

    def validate_deposit(self, application_account, value, operation_date=None):
        """
        Validate deposit data
        """
        application_settings = application_account.application.settings
        if value < application_settings.min_deposit:
            raise DepositValueError(
                {'value': f'O valor do depósito deve maior ou igual a {application_settings.min_deposit_str}'})

    def make_withdraw(self, operator, application_account, value, operation_type,
                      description=None, operation_date=None):
        """
        Unused
        """

    def validate_withdraw(self, application_account, value, operation_type, operation_date=None) -> None:
        """
        Unused
        """

    def close_application(self, operator, application_account,
                          description=None, operation_date=None):
        """
        Unused
        """
