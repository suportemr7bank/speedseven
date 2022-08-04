"""
Investment tables
"""

import django_tables2 as tables
from django.utils.safestring import mark_safe

from common.tables import MoneyColumn 

from . import models


class ApplicationAccountTable(tables.Table):
    """
    Application table
    """

    operations = tables.TemplateColumn(
        verbose_name='',
        template_name='investment/application_menu.html',
    )

    name = tables.Column(
        verbose_name='Cliente',
        accessor='user__get_full_name',
        order_by=('user__first_name', 'user__last_name')
    )

    user__email = tables.Column(verbose_name='Email')

    config = tables.TemplateColumn(
        verbose_name='',
        template_code="{% if record.application.has_account_settings %}"
                      "<a class='m-2' href='{% url \"investment:applicationaccount_settings\" record.id  %}'>"
                      "<i class='bi bi-gear'></i> </a>"
                      "{% else %}"
                      " <i class='bi bi-gear m-2 text-muted'></i> "
                      "{% endif %}"
    )

    application__product = tables.Column(verbose_name='Produto')

    class Meta:
        """ Meta class"""
        model = models.ApplicationAccount
        attrs = {"class": "table table-striped table-hover"}
        template_name = "django_tables2/bootstrap-responsive.html"
        fields = ('id', 'operations', 'config', 'application__product', 'application', 'name', 'user__email', 'operator',
                  'date_created', 'date_activated', 'date_deactivated', 'is_active')


class ApplicationOpTable(tables.Table):
    """
    Application operation table
    """

    application_account = tables.Column(
        verbose_name='Conta',
        accessor='application_account',
    )

    value = MoneyColumn()
    balance = MoneyColumn()

    class Meta:
        """ Meta class"""
        model = models.ApplicationOp
        attrs = {"class": "table table-striped table-hover"}
        template_name = "django_tables2/bootstrap-responsive.html"
        fields = ('id', 'application_account', 'application_account__application', 'operation_type',
                  'description', 'operation_date', 'value', 'balance')
        order_by = ('-operation_date')

class ApplicationModelTable(tables.Table):
    """
    Application model table
    """

    edit = tables.TemplateColumn(
        verbose_name='',
        template_code="<a href='{% url \"investment:applicationmodel_update\" record.id  %}'> <i class='bi bi-pencil-square'></i> </a>")

    class Meta:
        """ Meta class"""
        model = models.ApplicationModel
        attrs = {"class": "table table-striped table-hover"}
        template_name = "django_tables2/bootstrap-responsive.html"
        fields = ('id', 'edit', 'display_text',
                  'app_model_class', 'operator', 'date_created', 'is_active')


class ApplicationTable(tables.Table):
    """
    Application table
    """

    edit = tables.TemplateColumn(
        verbose_name='',
        template_code="<a href='{% url \"investment:application_update\" record.id  %}'>"
                      "<i class='bi bi-pencil-square'></i> </a>")

    config = tables.TemplateColumn(
        verbose_name='',
        template_code='{% if record.has_application_settings %}'
                      '<a href="{% url "investment:application_settings" record.id  %}"> <i class="bi bi-gear" title="Configurações"></i> </a>'
                      '{% else %}'
                      ' <i class="bi bi-gear text-muted" title="Configurações"></i> '
                      '{% endif %}'
    )

    income = tables.TemplateColumn(
        verbose_name='',
        template_code='<a href="{% url "investment:application_operation" record.id  %}">'
                      '<i class="bi bi-currency-dollar" title="Operações financeiras"></i> </a>')

    product = tables.Column(
        verbose_name='Produto'
    )

    is_active = tables.BooleanColumn(verbose_name="Diponivel para contratação")

    state = tables.Column(verbose_name='Situação', accessor='state')

    class Meta:
        """ Meta class"""
        model = models.Application
        attrs = {"class": "table table-striped table-hover"}
        template_name = "django_tables2/bootstrap-responsive.html"
        fields = ('id', 'edit', 'config', 'income', 'display_text', 'product', 'application_model', 
                  'date_created', 'date_activated', 'is_active', 'state')


class MoneyTransferBaseTable(tables.Table):
    """
    Application base model table
    """

    state = tables.Column(
        verbose_name='Situação'
    )

    product = tables.Column(verbose_name='Produto', empty_values=())

    receipt_file = tables.LinkColumn()

    receipt_file = tables.TemplateColumn(
        verbose_name='Comprovante',
        template_code="{% if record.receipt_file %}"
                      "<a href='{{record.receipt_file.url}}'> <i class='bi bi-file-text'></i> </a>"
                      "{% else %}"
                      "<i class='bi bi-file-text text-muted'></i>"
                      "{% endif %}",
        orderable=False)

    value = MoneyColumn()

    class Meta:
        """ Meta class"""
        model = models.MoneyTransfer
        attrs = {"class": "table table-striped table-hover"}
        template_name = "django_tables2/bootstrap-responsive.html"
        fields = ('product', 'operation', 'state', 'error_message',
                  'date_created', 'date_finished', 'value', 'receipt_file')
        order_by = ('-id')

    def render_product(self, value, record):
        """
        Try return the product name otherwise return applcation name
        """
        if getattr(record.application_account.application, 'product', None):
            return record.application_account.application.product.display_text
        else:
            return record.application_account.display_name


class MoneyTransferTable(MoneyTransferBaseTable):
    """
    Application model table
    """

    state = tables.TemplateColumn(
        verbose_name=mark_safe('<i class="bi bi-arrow-down-up"></i>'),
        template_code=("{% if record.state == 'CREA' %}"
                       "<i class='bi bi-clock' title='Aguardando'></i>"
                       "{% elif record.state == 'WTOP' %}"
                       " <i class='bi bi-clock' title='Aguardando operação'></i> "
                       "{% elif record.state == 'WREC' %}"
                       " <i class='bi bi-clock text-primary' title='Aguardando recibo'></i> "
                       "{% elif record.state == 'RUNN' %}"
                       " <i class='bi bi-play-circle text-primary' title='Em execuçao'></i> "
                       "{% elif record.state == 'FINI' %}"
                       " <i class='bi bi-check-circle text-success' title='Finalizado'></i> "
                       "{% elif record.state == 'ERRO' %}"
                       "<i class='bi bi-x-circle text-danger' title='{{record.error_message|default_if_none:'-----'}}'></i>"
                       "{% endif %}")
    )

    edit = tables.TemplateColumn(
        verbose_name='',
        template_code="{% if record.state == 'CREA' %}"
                      "<a href='{% url \"investment:moneytransfer_approval\" record.id  %}'>"
                      "<i class='bi bi-pencil-square'></i> </a>"
                      "{% else %}"
                      " <i class='bi bi-pencil-square text-muted'></i>"
                      "{% endif %}"
    )

    is_automatic = tables.TemplateColumn(
        verbose_name=mark_safe('<i class="bi bi-arrow-down-up"></i>'),
        template_code="{% if record.is_automatic %}"
                      " <i class='bi bi-robot' title='Tarefa automática'></i> "
                      "{% else %}"
                      "<i class='bi bi-person' title='Tarefa manual'></i>"
                      "{% endif %}"
    )

    value = MoneyColumn()

    class Meta:
        """ Meta class"""
        model = models.MoneyTransfer
        attrs = {"class": "table table-striped table-hover"}
        template_name = "django_tables2/bootstrap-responsive.html"
        fields = ('id', 'edit', 'is_automatic', 'state', 'application_account', 'operation',
                  'operator__get_full_name', 'approver__get_full_name', 'date_created', 'date_finished','value')
        exclude = ['product']
        order_by = ('-id')


class AccountOpScheduleTable(tables.Table):
    """
    Application account operation table
    """

    operation_date = tables.DateTimeColumn(
        verbose_name='Prazo',
        format='d/m/Y'
    )

    is_automatic = tables.TemplateColumn(
        verbose_name=mark_safe('<i class="bi bi-arrow-down-up"></i>'),
        template_code="{% if record.is_automatic %}"
                      " <i class='bi bi-robot' title='Tarefa automática'></i> "
                      "{% else %}"
                      "<i class='bi bi-person' title='Tarefa manual'></i>"
                      "{% endif %}"
    )

    edit = tables.TemplateColumn(
        verbose_name='',
        template_code="<a href='{% url \"investment:moneytransfer_completion\" record.money_transfer.id  %}'>"
                      "{% if record.state == 'FINI' or record.state == 'RUNN'  %}"
                      "<i class='bi bi-eye'></i>"
                      "{% else %}"
                      "<i class='bi bi-pencil-square'></i> </a>"
                      "{% endif %}"
    )

    state = tables.Column(verbose_name='Agendamento')

    money_transfer__value = MoneyColumn()

    class Meta:
        """ Meta class"""
        model = models.AccountOpSchedule
        attrs = {"class": "table table-striped table-hover"}
        template_name = "django_tables2/bootstrap-responsive.html"
        fields = (
            'id',
            'edit',
            'is_automatic',
            'state',
            'date_created',
            'money_transfer__application_account',
            'money_transfer__operation',
            'money_transfer__state',
            'operation_date',
            'money_transfer__value'
        )
        order_by = ('-id')


def bank_account_table(edit_view, exclude_owner=True):
    """
    Create a bank account table with specified edit view
    """
    class BankAccountTable(tables.Table):
        """
        Application operation table
        """

        edit = tables.TemplateColumn(
            verbose_name='',
            template_code=('<a href="{% url ' + f'"{edit_view}" record.id' + ' %}">' +
                           '<i class="bi bi-pencil-square"></i> </a>')
        )

        user = tables.Column(verbose_name='Cliente')

        class Meta:
            """ Meta class"""
            model = models.BankAccount
            attrs = {"class": "table table-striped table-hover"}
            fields = ['edit', 'user', 'bank', 'bank_branch_number', 'bank_branch_digit',
                      'account_number', 'account_digit', 'main_account', 'status']
            template_name = "django_tables2/bootstrap-responsive.html"
            if exclude_owner:
                exclude = ['user']

    return BankAccountTable
