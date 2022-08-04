"""
Pool account tables
"""


import django_tables2 as tables
from common.tables import PercentColumn
from .models import IncomeOperation

class IncomeOperationTable(tables.Table):
    """
    Income operation table
    """

    full_rate = PercentColumn()
    costs_rate = PercentColumn()
    net_rate = PercentColumn()
    paid_rate = PercentColumn()

    class Meta:
        """ Meta class"""
        model = IncomeOperation
        attrs = {"class": "table table-striped table-hover"}
        template_name = "django_tables2/bootstrap-responsive.html"
        order_by = ('-income_date')
