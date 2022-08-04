"""
Application operations
"""

from abc import ABC, abstractmethod
from ..models import AccountOpSchedule


class AbstractAccountOperation(ABC):
    """
    Wrapper class for application operation
    Isolate the application operation model from the interface
    """

    def schedule_operation(self, money_tranfer, operation_date, operator, is_automatic=False):
        """
        Schedule a deposit
        """
        # pylint: disable=no-member
        return AccountOpSchedule.objects.create(
            money_transfer=money_tranfer,
            operation_date=operation_date,
            operator=operator,
            is_automatic=is_automatic,
        )

    @abstractmethod
    def make_deposit(self, operator, application_account, value,
                     description=None, operation_date=None):
        """
        Make deposit
        """
    @abstractmethod
    def make_withdraw(self, operator, application_account, value, operation_type,
                      description=None, operation_date=None):
        """
        Make withdraw
        """

    @abstractmethod
    def close_application(self, operator, application_account,
                          description=None, operation_date=None):
        """
        Make a witdraw operation to reset balance and create a close operation
        """

    @abstractmethod
    def validate_deposit(self, application_account, value, operation_date=None) -> None:
        """
        Validate deposit data
        """

    @abstractmethod
    def validate_withdraw(self, application_account, value, operation_type, operation_date=None) -> None:
        """
        Validate witdraw data
        """
        
