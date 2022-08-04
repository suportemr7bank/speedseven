"""
Module for render tables
"""

import datetime

import django_tables2 as tables
from core import models as core_models
from products import models as products_models

class ReportTable(tables.Table):
    """
    Table with application operations
    """

    product = tables.Column(verbose_name='Produto')
    operation = tables.Column(verbose_name='Movimentação')
    date = tables.DateTimeColumn(verbose_name='Data', format='d/m/Y H:i:s')
    value = tables.Column(verbose_name='Valor (R$)')
    balance = tables.Column(verbose_name='Saldo (R%)')

    class Meta:
        """ Meta class"""
        attrs = {"class": "table table-striped table-hover"}
        template_name = "django_tables2/bootstrap-responsive.html"
        fields = ('product', 'operation', 'date', 'value', 'balance')

   # pylint: disable=unused-argument
    def __init__(self, *args, **kwargs):
        data = [
            {
                'product': 'Speed7',
                'operation': 'Aporte',
                'date': datetime.datetime(2022, 1, i, 10, 15+i, 1),
                'value': i*100,
                'balance': 11000+(i*100),
            } for i in [1, 2, 3, 4, 5, 6, 7]
        ]
        super().__init__(data=data)


class ProductPurchaseTable(tables.Table):
    """
    Product table
    """

    edit = tables.TemplateColumn(
        verbose_name='',
        template_code="<a href='{% url \"clients:products_purchase_update\" record.id  %}'> <i class='bi bi-pencil-square'></i> </a>")

    notify_before_end = tables.BooleanColumn(
        verbose_name='Notificar término', attrs={'td': {'class': 'text-center'}})
    auto_renew = tables.BooleanColumn(verbose_name='Renovar', attrs={
                                      'td': {'class': 'text-center '}})

    agreement = tables.TemplateColumn(
        verbose_name='Contrato',
        template_code="<a href='{% url \"clients:agreement_detail\" record.id  %}'> <i class='bi bi-file-text'></i> </a>")

    class Meta:
        """ Meta class"""
        model = products_models.ProductPurchase
        attrs = {"class": "table table-striped table-hover"}
        template_name = "django_tables2/bootstrap-responsive.html"
        fields = ('edit', 'product', 'agreement',
                  'date_purchased', 'date_expire', 'auto_renew', 'notify_before_end')


class AcceptanceTable(tables.Table):
    """
    User Acceptance table
    """
    view = tables.TemplateColumn(
        verbose_name='',
        template_code="<a href='{% url \"clients:acceptance_term_detail\" record.id  %}'> <i class='bi bi-file-text'></i> </a>")

    title = tables.Column(verbose_name='Termo')

    class Meta:
        """ Meta class"""
        model = core_models.AcceptanceTerm
        attrs = {"class": "table table-striped table-hover"}
        template_name = "django_tables2/bootstrap-responsive.html"
        fields = ('view', 'title' )
