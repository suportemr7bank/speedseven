
from django.urls import reverse_lazy

from core import tables
from core.forms.site import StartPageForm
from .core import CompanyListView, CompanyCreateView, CompanyUpdateView


class StartPageListView(CompanyListView):
    """
    Start page list
    """
    title = 'Página inicial'
    table_class = tables.StartPageTable
    controls = [
        {'link': {'text': 'Criar', 'url': 'core:start_page_create'}},
    ]


class StartPageCreateView(CompanyCreateView):
    """
    Create start page
    """
    title = 'Página inicial'
    form_class = StartPageForm

    success_url = reverse_lazy('core:start_page_list')
    cancel_url = success_url


class StartPageUpdateView(CompanyUpdateView):
    """
    Update start page
    """
    title = 'Página inicial'
    form_class = StartPageForm
    success_url = reverse_lazy('core:start_page_list')
    cancel_url = success_url
