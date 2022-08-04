"""
Module charts
"""

from http import HTTPStatus
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.generic import View

from charts.app_config import CHARTS_DEFAULT_JS_LIB

from .charts.base import AbstractDashboard


class   ChartJsonView(View):
    """
    Afford chart data
    """

    #pylint: disable=unused-argument
    def get(self, request, *args, **kwargs):
        """
        Rerturn char data according its id (html)
        """
        # pylint: disable=assignment-from-none
        dashboard = self.get_dashboard(request, *args, **kwargs)

        if dashboard:
            #pylint: disable=not-callable
            charts_data = dashboard(request).get_charts_data()
            charts = []
            for chart_data in charts_data:
                charts.append(
                    {
                        'div_id': chart_data.div_id,
                        'type': chart_data.chart.chart_type,
                        'data': chart_data.chart.get_json_data(request.theme)
                    }
                )

            return JsonResponse(
                {
                    'settings': {'chartlib': CHARTS_DEFAULT_JS_LIB},
                    'template': render_to_string(dashboard.template_name, request=request),
                    'charts': charts
                },
                status=HTTPStatus.OK)

        return JsonResponse({"error": 'Chart not found'}, status=HTTPStatus.NOT_FOUND)

    def get_dashboard(self, request, *args, **kwargs) -> AbstractDashboard:
        """
        Return dashboard
        """
        return None
