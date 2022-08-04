"""
    Module for tables
"""

import django_tables2 as tables
from investorprofile import models as invprov_models

from . import models


class ProductTable(tables.Table):
    """
    Product table
    """
    edit = tables.TemplateColumn(
        verbose_name='',
        template_code="<a href='{% url \"products:product_update\" record.id  %}'>"
                      "<i class='bi bi-pencil-square'></i> </a>")

    is_active = tables.BooleanColumn(
        verbose_name='Ativo'
    )

    class Meta:
        """ Meta class"""
        model = models.Product
        attrs = {"class": "table table-striped table-hover"}
        template_name = "django_tables2/bootstrap-responsive.html"
        fields = ('edit', 'name', 'display_text', 'category',
                  'application', 'date_created', 'is_active')


class ProductPurchaseTable(tables.Table):
    """
    Product table
    """
    agreement = tables.TemplateColumn(
        verbose_name='Contrato',
        template_code="<a href='{% url \"products:agreement_detail\" record.id  %}'> <i class='bi bi-file-text'></i> </a>",
        orderable=False)

    product__display_text = tables.Column(verbose_name='Produto')

    notify_before_end = tables.BooleanColumn(
        verbose_name='Notificar vencimento'
    )

    class Meta:
        """ Meta class"""
        model = models.ProductPurchase
        attrs = {"class": "table table-striped table-hover"}
        template_name = "django_tables2/bootstrap-responsive.html"
        fields = ('id', 'application_account', 'product__display_text', 'agreement_template',
                  'agreement', 'auto_renew', 'date_purchased', 'date_expire', 'notify_before_end')


class ProductDashboardTable(tables.Table):
    """
    Product dashboard table
    """
    edit = tables.TemplateColumn(
        verbose_name='',
        template_code="<a href='{% url \"products:product_dashboard_update\" record.id  %}'> <i class='bi bi-pencil-square'></i> </a>")

    class Meta:
        """ Meta class"""
        model = models.ProductDashboard
        attrs = {"class": "table table-striped table-hover"}
        template_name = "django_tables2/bootstrap-responsive.html"
        fields = ('edit', 'product', 'dashboard')


class AgreementTable(tables.Table):
    """
    Agreement table
    """
    edit = tables.TemplateColumn(
        verbose_name='',
        template_code="<a href='{% url \"products:agreement_update\" record.id  %}'> <i class='bi bi-pencil-square'></i> </a>")

    preview = tables.TemplateColumn(
        verbose_name='Visualização',
        template_code="<a href='{% url \"products:agreement_preview\" record.id  %}'> <i class='bi bi-file-text'></i> </a>")

    id = tables.Column(verbose_name='ID')

    term = tables.Column(verbose_name="Prazo",
                         empty_values=[], orderable=False)

    type = tables.Column(verbose_name='Tipo')

    class Meta:
        """ Meta class"""
        model = models.AgreementTemplate
        attrs = {"class": "table table-striped table-hover"}
        template_name = "django_tables2/bootstrap-responsive.html"
        fields = ('edit', 'id', 'display_text', 'preview', 'product', 'type',
                  'date_created', 'date_changed')

    def render_term(self, value, record):
        """
        Agreement term
        """
        term = record.term_value
        if not term:
            return 'Indeterminado'
        else:
            return f'{term} {record.get_term_unit_display()}'


class DashboardTable(tables.Table):
    """
    Product table
    """
    edit = tables.TemplateColumn(
        verbose_name='',
        template_code="<a href='{% url \"products:dashboard_update\" record.id  %}'> <i class='bi bi-pencil-square'></i> </a>")

    class Meta:
        """ Meta class"""
        model = models.Dashboard
        attrs = {"class": "table table-striped table-hover"}
        template_name = "django_tables2/bootstrap-responsive.html"
        fields = ('edit', 'display_text', 'dashboard_class', 'description')


class ProfileProductTable(tables.Table):
    """
    Product table
    """
    edit = tables.TemplateColumn(
        verbose_name='',
        template_code="<a href='{% url \"products:profile_product_update\" record.id  %}'> <i class='bi bi-pencil-square'></i> </a>"
    )

    products = tables.Column(
        verbose_name='Produtos associados', empty_values=(), orderable=False)
    display_text = tables.Column(verbose_name='Perfil de investimento')

    class Meta:
        """ Meta class"""
        model = invprov_models.Profile
        attrs = {"class": "table table-striped table-hover"}
        template_name = "django_tables2/bootstrap-responsive.html"
        fields = ('edit', 'display_text', 'products')

    def render_products(self, value, record):
        """
        Render the profile products
        """
        products = list(models.ProfileProduct.objects.filter(
            profile=record).order_by('product__display_text').values_list('product__display_text', flat=True))
        return " | ".join(products)


class ProductCategoryTable(tables.Table):
    """
    ProductCategory table
    """
    edit = tables.TemplateColumn(
        verbose_name='',
        template_code="<a href='{% url \"products:category_update\" record.id  %}'>"
                      "<i class='bi bi-pencil-square'></i> </a>")

    class Meta:
        """ Meta class"""
        model = models.ProductCategory
        attrs = {"class": "table table-striped table-hover"}
        template_name = "django_tables2/bootstrap-responsive.html"
        fields = ('edit', 'name', 'display_text', 'date_created', 'show_title')


class CategoryDocumentTable(tables.Table):
    """
    Category document table
    """
    edit = tables.TemplateColumn(
        verbose_name='',
        template_code="<a href='{% url \"products:category_document_update\" record.id  %}'>"
                      "<i class='bi bi-pencil-square'></i> </a>")

    class Meta:
        """ Meta class"""
        model = models.CategoryDocument
        attrs = {"class": "table table-striped table-hover"}
        template_name = "django_tables2/bootstrap-responsive.html"
        fields = ('edit', 'name', 'display_text', 'category', 'date_created')
