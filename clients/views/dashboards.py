"""
Dashboard JSON view
"""

from charts.views import ChartJsonView
from accounts.auth import mixins as auth_mixin

from products.models import ProductDashboard


class ClientDashboardJson(auth_mixin.LoginRequiredMixin, ChartJsonView):
    """
    Dashboars charts data in JSON format
    """

    #pylint: disable=unused-argument
    def get_dashboard(self, request, *args, **kwargs):
        """
        Get product charts according to the purchase id
        Each product may have a specific collection of charts (dashboard)
        """
        purchase_id = self.request.GET.get('purchase', None)

        if purchase_id:
            # pylint: disable=no-member
            try:
                product_dashboard = ProductDashboard.objects.get(
                    product__productpurchase__id=purchase_id)
                if product_dashboard:
                    return product_dashboard.dashboard.get_class()
            except ProductDashboard.DoesNotExist:
                pass

        return None
