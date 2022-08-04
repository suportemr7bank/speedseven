"""
Aplication tasks
"""

from celery import shared_task
from celery.utils.log import get_task_logger

from .models import IncomeOperation
from .income import IncomeCalculation

def notify_progress(message):
    """
    Notify calculation progress
    """
    # TODO: implement websocket

@shared_task
def run_income_operation(income_operation_pk):
    """
    Run income operation in background
    """
    logger = get_task_logger(__name__)

    # pylint: disable=no-member
    income_operation = IncomeOperation.objects.get(pk=income_operation_pk)
    IncomeCalculation.run_income_operation(income_operation, notify_progress)
