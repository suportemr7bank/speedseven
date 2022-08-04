"""
Apexchart.js implementation
"""

from dataclasses import dataclass
from .base import AbstractChart, ChartDataType


@dataclass
class LineChart(AbstractChart):
    """
    Base class to buid chart
    """
    series: dict
    x_axis: list

    chart_type = ChartDataType.CHART

    def get_json_data(self, theme=None):
        """
        Json data to javascript chart library
        """

        return {
            'series': self.series,
            'chart': {
                'type': 'line',
                'height': '100%',
                'zoom': {
                    'enabled': False
                },
                'background': 'transparent',

            },
            'dataLabels': {
                'enabled': False
            },
            'stroke': {
                'curve': 'straight',
                'width': 3,
            },
            'title': {
                'text': self.title,
                'align': 'left',
            },
            'xaxis': {
                'categories': self.x_axis,
            },
            'theme': {
                'mode': theme,
            }
        }


@dataclass
class DoughnutChart(AbstractChart):
    """
    Default doughnut chart
    """
    data: dict
    labels: list

    chart_type = ChartDataType.CHART

    def get_json_data(self, theme=None):
        return {
            'series': self.data,
            'labels': self.labels,
            'chart': {
                'type': 'donut',
                'height': '100%',
            },
            'legend': {
                'position': 'bottom'
            },
            'responsive': [{
                'breakpoint': 300,
                'options': {
                    'chart': {
                        'width': 300
                    },
                    'legend': {
                        'position': 'bottom'
                    }
                }
            }],
            'plotOptions': {
                'pie': {
                    'customScale': 1
                }
            },
            'tooltip': {
                'enabled': False,
            },
            'title': {
                'text': self.title,
                'align': 'left'
            },
        }
