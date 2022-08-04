
"""
Pool account views
"""

from common.views import mixins
from .models import IncomeOperation

from . import tables

class IncomeOperationListView(mixins.AdminMixin, mixins.ListViewMixin):
    """
    Income list
    """
    model = IncomeOperation
    table_class = tables.IncomeOperationTable
    template_name = 'common/list.html'
    title = 'Operações de rendimento'
