"""
    Charts factory
"""

from django.core.exceptions import ImproperlyConfigured

from charts.charts.base import CharData

from .app_config import CHARTS_DEFAULT_JS_LIB
from .charts import generic
from .charts.config import ChartsAvailable

if CHARTS_DEFAULT_JS_LIB == ChartsAvailable.APEXCHART:
    from charts.charts import apexcharts as charts_collection
else:
    raise ImproperlyConfigured(
        f'CHARTS_DEFAULT_JS_LIB={CHARTS_DEFAULT_JS_LIB} is not valid')


class ChartFactory:
    """
    Factory form chart creation
    """

    @staticmethod
    def card(div_id, title, text):
        """
        Create a bootstrap5 card like item
        """
        card_data = generic.Card(title, text)
        return CharData(div_id, card_data)

    @staticmethod
    def line_chart(div_id, title, series, x_axis):
        """
        Create a line chart
        """
        line_chart = charts_collection.LineChart(title, series, x_axis)
        return CharData(div_id, line_chart)

    @staticmethod
    def doughnut_chart(div_id, title, data, labels):
        """
        Create a doughut chart
        """
        doughnut_chart = charts_collection.DoughnutChart(title, data, labels)
        return CharData(div_id, doughnut_chart)
