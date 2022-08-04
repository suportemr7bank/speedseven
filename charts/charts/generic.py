"""
Generic elements which not belong to any lib or not is a plot

"""

from dataclasses import dataclass

from charts.charts.base import AbstractChart, ChartDataType


@dataclass
class Card(AbstractChart):
    """
    Card element. Only title and text (not a plot)
    """

    text: str = ""
    chart_type = ChartDataType.CARD

    def get_json_data(self, theme=None):
        """
        Json data to javascript chart library
        """

        return f'''
            <div class="card">
                <div class="h5 text-success">{self.title}</div>
                <div class="h4">{self.text}</div>
            </div>
            '''