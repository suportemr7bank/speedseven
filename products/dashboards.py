"""
Product Dashboards
"""

from charts.charts.base import AbstractDashboard
from charts.factory import ChartFactory


class ProductDashboardMixin:
    """
    Some common methods
    """

    def _cards(self):
        return [
            ChartFactory.card('card_id1', 'Média Speed7', '1%'),
            ChartFactory.card('card_id2', 'Média Reddex', '1,04%'),
            ChartFactory.card('card_id3', 'Média Dupper7', '1,08%'),
        ]


class ProductsDashboard(ProductDashboardMixin, AbstractDashboard):
    """
    Low riskproduct data
    """

    dashboard_id = 'products'
    name = 'Comparação entre rentabilidades (%)'
    template_name = 'core/dashboards/products_dash.html'

    def get_charts_data(self):
        return [
            self._comparison(),
        ] + self._cards()

    def _comparison(self):
        value_1 = [1, 1, 1, 1, 1]
        value_2 = [1, 0.85, 0.85, 1.2, 1.3]
        value_3 = [0.8, 1.5, 1.4, 0.5, 1.2]

        chart = ChartFactory.line_chart(
            'line_chart_id1',
            self.name,
            [
                {'name': 'Speed7', 'data': value_1},
                {'name': 'Reddex', 'data': value_2},
                {'name': 'Duper7', 'data': value_3},
            ],
            ['10/2021 ', '11/2021', '12/2021', '1/2022', '2/2022']
        )
        return chart
