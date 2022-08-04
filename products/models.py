"""
Products models
"""

from collections import OrderedDict
import pydoc

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.db import models
from django.utils import timezone
from tinymce import models as tinymce_models

from investorprofile import models as invprof_models
from investment import models as invest_models


class ProductCategory(models.Model):
    """
    Product category allow product grouping according some defined critetia
    """

    class Meta:
        """
        Meta class
        """
        verbose_name = 'Categoria de produto'
        verbose_name_plural = 'Categorias de produtos'

    name = models.CharField(
        max_length=64, verbose_name='Nome', help_text="Apenas para controle interno")

    title = models.CharField(
        max_length=64, verbose_name='Título')

    date_created = models.DateTimeField(
        verbose_name='Data de criação', auto_now_add=True, editable=False)

    briefing = models.TextField(
        verbose_name="Descrição breve da categoria",
        help_text="Apenas para controle interno",
        null=True, blank=True)

    show_title = models.BooleanField(
        verbose_name='Mostrar título', default=True)

    def __str__(self) -> str:
        return str(self.title)


class CategoryDocument(models.Model):
    """
    Category documents
    """

    class Meta:
        """
        Meta class
        """
        verbose_name = 'Documento da categoria'
        verbose_name_plural = 'Documentos das categorias'

    name = models.CharField(max_length=64, verbose_name='Nome')
    display_text = models.CharField(
        max_length=64, verbose_name='texto de exibição')
    category = models.ForeignKey(
        ProductCategory, verbose_name='Categoria', on_delete=models.CASCADE)
    text = tinymce_models.HTMLField(
        verbose_name='Texto do documento')
    date_created = models.DateTimeField(
        verbose_name='Data de criação', auto_now_add=True, editable=False)

    def __str__(self) -> str:
        return f'{self.category.display_text} - {self.display_text}'


class Product(models.Model):
    """
    Platform products
    """

    class Meta:
        """
        Meta class
        """
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'

    name = models.CharField(max_length=64, verbose_name='Nome')
    display_text = models.CharField(
        max_length=64, verbose_name='Texto de exibição')
    application = models.OneToOneField(
        invest_models.Application, verbose_name='Aplicação',
        help_text='Deve haver somente uma aplicação por produto',
        on_delete=models.CASCADE)

    category = models.ForeignKey(
        ProductCategory, verbose_name='Categoria', on_delete=models.CASCADE,
        null=True, blank=True)

    date_created = models.DateTimeField(
        verbose_name='Data de criação', auto_now_add=True, editable=False)

    briefing = tinymce_models.HTMLField(
        verbose_name="Informação resumida para o cliente",
        help_text="Mostrado ao cliente na oferta de produtos",
        null=True, blank=True)

    info = tinymce_models.HTMLField(
        verbose_name='Informação para o cliente',
        null=True, blank=True)

    @property
    def is_active(self):
        """
        Produtc is active if application is active
        """
        if self.application:
            return self.application.is_active
        return False

    @staticmethod
    def group_by_category(products):
        """
        Group products by categories
        { category_obj : [Products...], ...}
        """

        categories = OrderedDict()

        for product in products:
            category = product.category
            if not categories.get(category):
                categories[category] = []
                categories[category].append(product)
            else:
                categories[category].append(product)

        for category, _value in categories.items():
            if not categories[category]:
                del categories[category]

        return categories

    def __str__(self) -> str:
        return str(self.display_text)


class AgreementTemplate(models.Model):
    """
    Platform aggrements
    """

    TERM_UNIT_DAY = 'D'
    TERM_UNIT_MONTH = 'M'
    TERM_UNIT_YEAR = 'Y'

    TERM_CHOICES = (
        (TERM_UNIT_DAY, 'Dia'),
        (TERM_UNIT_MONTH, 'Mês'),
        (TERM_UNIT_YEAR, 'Ano'),
    )

    class Type(models.TextChoices):
        """
        Client type
        """
        PF = 'PF', 'Pessoa física'
        PJ = 'PJ', "Pessoa jurídica"

    class Meta:
        """
        Meta class
        """
        verbose_name = 'Contrato'
        verbose_name_plural = 'Contratos'

    name = models.CharField(max_length=64, verbose_name='Nome')

    type = models.CharField(
        max_length=2, verbose_name='Pessoa física/jurídica', choices=Type.choices, default=Type.PF)

    product = models.ForeignKey(Product, verbose_name='Produto',
                                null=True, blank=True, on_delete=models.CASCADE)
    display_text = models.CharField(
        max_length=64, verbose_name='Texto de exibição')
    text = tinymce_models.HTMLField(verbose_name='Texto do contrato')
    instruction = models.TextField(
        verbose_name='Instruções', help_text="Exclusivo para criação de contrato",
        null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True,
                                        verbose_name='Data de criação', editable=False)
    date_changed = models.DateTimeField(
        verbose_name='Última atualização', auto_now=True, editable=False)

    term_unit = models.CharField(
        max_length=1, verbose_name="Unidade de tempo",
        default=TERM_UNIT_MONTH, choices=TERM_CHOICES, null=True, blank=True)

    term_value = models.IntegerField(
        verbose_name='Duração do contrato', help_text='Deixe em branco para prazo indefinido',
        null=True, blank=True)

    @property
    def term_str(self):
        """
        Agreement term string
        """
        if self.term_unit is None or self.term_value is None:
            return None

        unit = ''
        if self.term_value == 1:
            unit = self.get_term_unit_display()
        else:
            if self.term_unit == self.TERM_UNIT_MONTH:
                unit = 'Mêses'
            else:
                unit = self.get_term_unit_display() + 's'

        return f'{self.term_value} {unit}'

    @property
    def term(self):
        """
        Agreement term
        """
        term_value = self.term_value
        if not term_value:
            return None

        term = timezone.localtime(timezone.now())
        term_unit = self.term_unit
        if term_unit == self.TERM_UNIT_DAY:
            term = timezone.timedelta(days=term_value)
        elif term_unit == self.TERM_UNIT_MONTH:
            term = relativedelta(months=term_value)
        elif term_unit == self.TERM_UNIT_YEAR:
            term = relativedelta(years=term_value)

        return term

    def __str__(self) -> str:
        return str(self.display_text)


class ProductPurchase(models.Model):
    """
    Product pruchase
    """

    class Meta:
        """
        Meta class
        """
        verbose_name = 'Produto contratado'
        verbose_name_plural = 'Produtos contratados'

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product, verbose_name='Produto', on_delete=models.CASCADE)
    application_account = models.OneToOneField(
        invest_models.ApplicationAccount, verbose_name='Conta',
        null=True, blank=True, on_delete=models.CASCADE)
    agreement_template = models.ForeignKey(
        AgreementTemplate, verbose_name='Modelo do contrato', on_delete=models.CASCADE)
    agreement = models.TextField(verbose_name='Contrato')
    auto_renew = models.BooleanField(
        verbose_name='Renovação automática', default=False)
    date_purchased = models.DateTimeField(
        verbose_name='Data de aquisição', auto_now_add=True)
    date_expire = models.DateTimeField(
        verbose_name='Vencimento', null=True, blank=True)
    date_cancelled = models.DateTimeField(
        verbose_name='Cancelamento', null=True, blank=True, editable=False)
    notify_before_end = models.BooleanField(
        verbose_name='Notificar antes do término do contrato', default=False)


class Dashboard(models.Model):
    """
    Available dashboards
    """
    class Meta:
        """
        Meta class
        """
        verbose_name = 'Dashboard'

    display_text = models.CharField(
        max_length=64, verbose_name="Nome de exbição")

    application = models.CharField(
        max_length=128, verbose_name='Aplicação')

    dashboard_class = models.CharField(
        max_length=128, verbose_name='Classe do dashboard')

    description = models.TextField(
        verbose_name='Descrição', null=True, blank=True)

    # TODO: try to cache
    def get_class(self):
        """
        Get the dashboard python class
        """
        return pydoc.locate(f'{self.application}.dashboards.{str(self.dashboard_class)}')

    def __str__(self) -> str:
        return str(self.display_text)


class ProductDashboard(models.Model):
    """
    Relates dashboard with producsts
    """

    class Meta:
        """
        Meta class
        """
        verbose_name = 'Dashboard do produto'
        verbose_name = 'Dashboard dos produtos'
        constraints = [
            models.UniqueConstraint(
                fields=['product', 'dashboard'], name='unique_product_dashboard')
        ]

    product = models.OneToOneField(
        Product,
        verbose_name='Produto relacionado ao dashboard',
        on_delete=models.CASCADE)

    dashboard = models.ForeignKey(
        Dashboard, verbose_name='Dashboard', on_delete=models.CASCADE)

    def __str__(self) -> str:
        # pylint: disable=no-member
        return f'{self.product.display_text} - {self.dashboard.display_text}'


class ProfileProduct(models.Model):
    """
    Product investor profile
    Products will be presented to tho user according to the user investor profile
    """

    class Meta:
        """
        Meta class
        """
        verbose_name = 'Perfil do produto'
        verbose_name_plural = 'Perfís dos produtos'

    product = models.ForeignKey(
        Product, verbose_name='Produto', on_delete=models.CASCADE)
    profile = models.ForeignKey(
        invprof_models.Profile, verbose_name='Perfil de investimento', on_delete=models.CASCADE)

    def __str__(self) -> str:
        # pylint: disable=no-member
        return f'{self.product.display_text} - {self.profile.display_text}'
