
"""
Crowd funding account views
"""

from django.shortcuts import get_object_or_404
from common.views import mixins

from . import tables
from .models import ApplicationDeposit, ApplicationSettings


class ApplicationDepositListView(mixins.AdminMixin, mixins.ListViewMixin):
    """
    Income list
    """
    model = ApplicationDeposit
    table_class = tables.ApplicationDepositTable
    template_name = 'common/list.html'
    title = 'Lista de depósitos'

    def __init__(self) -> None:
        super().__init__()
        self.application_pk = None

    def get(self, request, *args, **kwargs):
        app_settings = get_object_or_404(ApplicationSettings, pk=kwargs['pk'])
        self.application_pk = app_settings.application.pk
        application = app_settings.application.display_text

        product_str = "Aplicação sem produto associado"
        if product := getattr(app_settings.application, 'product', None):
            product_str = product.display_text

        self.header_message = f'Aplicação - {application} <br> Produto associado - {product_str}'
        return super().get(request, *args, *kwargs)

    def get_queryset(self):
        return super().get_queryset().filter(
            application_account__application__pk=self.application_pk)
