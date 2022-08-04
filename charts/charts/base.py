
"""
Chart defaul types
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List

from django.http import HttpRequest


class ChartDataType:
    """
    Chart types
    """
    NONE = 'none'
    CHART = 'chart'
    CARD = 'card'


@dataclass
class AbstractChart(ABC):
    """
    Base class to buid chart json data
    """
    title: str
    chart_type = ChartDataType.NONE

    @abstractmethod
    def get_json_data(self, theme=None):
        """
        Chart in specific format according chart type
        """


@dataclass
class CharData:
    """
    Encapsulates chart data
    This data is passed as a json to request
    """

    div_id: str = None
    chart: AbstractChart = None


@dataclass
class AbstractDashboard(ABC):
    """
    Base class for product data for charts
    """
    dashboard_id = None
    name = None
    template_name = None
    request: HttpRequest

    @abstractmethod
    def get_charts_data(self) -> List[CharData]:
        """
        Return data as dicit to build charts
        """
