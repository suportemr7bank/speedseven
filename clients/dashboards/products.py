"""
Product Dashboards
"""

from charts.charts.base import AbstractDashboard
from charts.factory import ChartFactory
from common import numbers


class ProductDashboardMixin:
    """
    Some common methods
    """

    def _cards(self):
        return [
            ChartFactory.card('card_id1', 'Total', 'R$17.500,00'),
            ChartFactory.card('card_id2', 'Movimentação', 'R$-500,00'),
            ChartFactory.card('card_id3', 'Rendimentos', 'R$500,00'),
        ]

    def _investsments(self):
        chart = ChartFactory.doughnut_chart(
            'line_chart_id1',
            'Capital investido',
            [10000, 2500, 5000, 2000],
            ['CS7 - R$2500', 'RED - R$10000',  '(DU7) - R$2000', 'Líquido - R$5000']
        )
        return chart


class LowRiskProductDashboard(ProductDashboardMixin, AbstractDashboard):
    """
    Low riskproduct data
    """

    dashboard_id = 'low_risk'
    name = 'Carteira Speed7 (CS7)'
    template_name = 'clients/start/low_risk_dash.html'

    def get_charts_data(self):
        return [
            self._investsments(),
            self._forecast(),
        ] + self._cards()

    def _forecast(self):
        initial_1 = 10000
        initial_2 = 12500
        rate_1 = 0.01
        rate_2 = 0.005
        value_1 = []
        value_2 = []
        value_3 = []
        for month in range(0, 13, 3):
            value_1.append(numbers.truncate_decimal_2(initial_1*(1+rate_1)**month))
            value_2.append(numbers.truncate_decimal_2(initial_2*(1+rate_1)**month))
            value_3.append(numbers.truncate_decimal_2(initial_2*(1+rate_2)**month))

        chart = ChartFactory.line_chart(
            'line_chart_id2',
            'Projeção comparativa anual - ' + self.name,
            [
                {'name': 'speed7 - bloqueado', 'data': value_1},
                {'name': 'speed7 - líquido', 'data': value_2},
                {'name': '0,5% - liquido', 'data': value_3},
            ],
            ['1/2022 ', '3/2022', '6/2022', '9/2020', '12/2022']
        )
        return chart


class MediumRiskProductDashboard(ProductDashboardMixin, AbstractDashboard):
    """
    Low riskproduct data
    """

    dashboard_id = 'medium_risk'
    name = 'Reddex (RED)'
    template_name = 'clients/start/low_risk_dash.html'

    def get_charts_data(self):
        return [
            self._investsments(),
            self._forecast()
        ] + self._cards()

    def _forecast(self):
        initial_1 = 10000
        initial_2 = 15000
        rate_1 = 0.015
        rate_2 = 0.005
        value_1 = []
        value_2 = []
        value_3 = []
        for month in range(0, 13, 3):
            value_1.append(numbers.truncate_decimal_2(initial_1*(1+rate_1)**month))
            value_2.append(numbers.truncate_decimal_2(initial_2*(1+rate_1)**month))
            value_3.append(numbers.truncate_decimal_2(initial_2*(1+rate_2)**month))

        chart = ChartFactory.line_chart(
            'line_chart_id2',
            'Projeção comparativa anual - ' + self.name,
            [
                {'name': 'speed7 - bloqueado', 'data': value_1},
                {'name': 'speed7 - líquido', 'data': value_2},
                {'name': '0,5% - liquido', 'data': value_3},
            ],
            ['1/2022 ', '3/2022', '6/2022', '9/2020', '12/2022']
        )
        return chart


class HighRiskProductDashboard(ProductDashboardMixin, AbstractDashboard):
    """
    High risk product data
    """

    dashboard_id = 'high_risk'
    name = 'Dupper7 (DU7) '
    template_name = 'clients/start/high_risk_dash.html'

    def get_charts_data(self):
        return [
            self._investsments(),
            self._rates(),
            self._gains(),
            self._gains2(),
        ] + self._cards()

    def _rates(self):
        rates = [1.3, 1.7, 0.5, 2.3, 2.0, 1.2]

        chart = ChartFactory.line_chart(
            'line_chart_id2',
            'Rentabilidade (%)- ' + self.name,
            [
                {'name': 'Rentabilidade (%)', 'data': rates},
            ],
            ['1/2022 ', '2/2022', '3/2022', '4/2020', '5/2022', '6/2022']
        )
        return chart

    def _gains(self):
        gains = [1000, 500, 2000, 100, 300, 3000]

        chart = ChartFactory.line_chart(
            'line_chart_id3',
            'Rendimento (R%) ' + self.name,
            [
                {'name': 'Granho (R$)', 'data': gains},
            ],
            ['1/2022 ', '2/2022', '3/2022', '4/2020', '5/2022', '6/2022']
        )
        return chart

    def _gains2(self):
        gains = [1000, 500, 2000, 100, 300, 3000]

        chart = ChartFactory.line_chart(
            'line_chart_id4',
            'Rendimento (R$) ' + self.name,
            [
                {'name': 'Granho (R$)', 'data': gains},
            ],
            ['1/2022 ', '2/2022', '3/2022', '4/2020', '5/2022', '6/2022']
        )
        return chart
