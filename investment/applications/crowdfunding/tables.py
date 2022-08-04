"""
Crowdfunding account tables
"""


import django_tables2 as tables
from .models import ApplicationDeposit

class ApplicationDepositTable(tables.Table):
    """
    Income operation table
    """

    value = tables.Column(accessor='value_str')

    class Meta:
        """ Meta class"""
        model = ApplicationDeposit
        attrs = {"class": "table table-striped table-hover"}
        template_name = "django_tables2/bootstrap-responsive.html"
