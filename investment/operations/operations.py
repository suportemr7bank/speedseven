"""
Application operations
"""

from ..models import ApplicationOp
from ..interfaces.operations import AbstractAccountOperation


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
        return ApplicationOp.make_deposit(
            operator, application_account, value, description, operation_date)

    def make_withdraw(self, operator, application_account, value, operation_type,
                      description=None, operation_date=None):
        """
        Make a withdraw
        """
        return ApplicationOp.make_withdraw(
            application_account, operator, value, operation_type, description, operation_date)

    def close_application(self, operator, application_account,
                          description=None, operation_date=None):
        """
        Make a witdraw operation to reset balance and create a close operation
        """
        #pylint: disable=no-member
        return ApplicationOp.close_application(operator, application_account,
                                               description, operation_date)

    def validate_deposit(self, application_account, value, operation_date=None):
        """
        Validate deposit data
        """
        ApplicationOp.validate_deposit(
            application_account, value, operation_date)

    def validate_withdraw(self, application_account, value, operation_type, operation_date=None):
        """
        Validate witdraw data
        """
        ApplicationOp.validate_withdraw(
            application_account, value, operation_type, operation_date)
