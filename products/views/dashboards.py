"""
Dashboard JSON view
"""

from charts.views import ChartJsonView
from accounts.auth import mixins as auth_mixin

from .. import dashboards as d


class ProductsDashboardJson(auth_mixin.LoginRequiredMixin, ChartJsonView):
    """
    Dashboars charts data in JSON format
    """

    #pylint: disable=unused-argument
    def get_dashboard(self, request, *args, **kwargs):
        """
        Dashboard data
        """
        return d.ProductsDashboard
