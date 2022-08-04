"""
    Module for tables
"""


import django_tables2 as tables
from django.contrib.sites.models import Site
from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse
from django.utils.html import format_html

from accounts.roles import Roles
from clients import models as clients_models

from core import models as core_models


class UserTable(tables.Table):
    """
    User table
    """

    edit = tables.TemplateColumn(
        verbose_name='',
        template_code="<a href='{% url \"core:user_update\" record.id  %}'> <i class='bi bi-pencil-square'></i> </a>")
    email = tables.Column(verbose_name='Email')
    name = tables.Column(
        verbose_name='Nome',
        accessor='get_full_name',
        order_by=('first_name', 'last_name'))
    role = tables.Column(verbose_name='Papel',
                         empty_values=(), orderable=False)

    investorprofile__profile__display_text = tables.Column(
        verbose_name='Perfil de investimento')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.choices = dict(Roles.choices)

    class Meta:
        """ Meta class"""
        model = core_models.User
        attrs = {"class": "table table-striped table-hover"}
        template_name = "django_tables2/bootstrap-responsive.html"
        fields = ('edit', 'id', 'name', 'email', 'role',
                  'investorprofile__profile__display_text', 'date_joined', 'is_active')

    # pylint: disable=unused-argument
    def render_role(self, value, record):
        """
        User role list
        """
        roles = list(record.userrole_set.values_list('role', flat=True))
        return ', '.join(self._to_display_text(roles))

    def _to_display_text(self, roles):
        if self.choices:
            return [self.choices.get(value, 'Error') for value in roles]
        return []


class AdminTable(tables.Table):
    """
    Admin table
    """
    edit = tables.TemplateColumn(
        verbose_name='',
        template_code="<a href='{% url \"core:admin_update\" record.id  %}'> <i class='bi bi-pencil-square'></i> </a>")
    email = tables.Column(verbose_name='Email')
    name = tables.Column(verbose_name='Nome',
                         accessor='get_full_name',
                         order_by=('first_name', 'last_name'))

    class Meta:
        """ Meta class"""
        model = core_models.User
        attrs = {"class": "table table-striped table-hover"}
        template_name = "django_tables2/bootstrap-responsive.html"
        fields = ('edit', 'id', 'name', 'email', 'date_joined', 'is_active')


class AcceptanceTable(tables.Table):
    """
    Agreement table
    """
    edit = tables.TemplateColumn(
        verbose_name='',
        template_code="<a href='{% url \"core:acceptance_term_update\" record.id  %}'> <i class='bi bi-pencil-square'></i> </a>")

    class Meta:
        """ Meta class"""
        model = core_models.AcceptanceTerm
        attrs = {"class": "table table-striped table-hover"}
        template_name = "django_tables2/bootstrap-responsive.html"
        fields = ('edit', 'title', 'type', 'version', 'date_created',
                  'date_changed', 'is_active')


class ClientsTable(tables.Table):
    """
    Admin table
    """
    edit = tables.TemplateColumn(
        verbose_name='',
        template_code="<a href='{% url \"core:client_update\" record.id  %}'> <i class='bi bi-pencil-square'></i> </a>")

    user__email = tables.Column(verbose_name='Email')

    name = tables.Column(verbose_name='Nome', accessor='get_full_name')

    user__date_joined = tables.Column(verbose_name='Início do relacionamento')

    class Meta:
        """ Meta class"""
        model = clients_models.Client
        attrs = {"class": "table table-striped table-hover"}
        template_name = "django_tables2/bootstrap-responsive.html"
        fields = ('edit', 'id', 'name', 'user__email',
                  'phone', 'type', 'user__date_joined', 'birth_date')


class EmailBatchTable(tables.Table):
    """
    Admin table
    """

    edit = tables.TemplateColumn(
        verbose_name='',
        template_code="<a href='{% url \"core:email_detail\" record.id  %}'> <i class='bi bi-pencil-square'></i> </a>"
    )

    logs = tables.Column(verbose_name='Logs', empty_values=())

    role = tables.Column(verbose_name='Enviado para')
    date_created = tables.DateTimeColumn(format='d/m/Y H:i:s')
    date_finished = tables.DateTimeColumn(
        format='d/m/Y H:i:s',
        attrs={
            'td': {
                'id': lambda value, record: f"id_{record.id}_date_finished"
            }
        }
    )
    sent = tables.Column(attrs={
        'td': {
            'id': lambda value, record: f"id_{record.id}_sent"
        }
    })
    status = tables.Column(attrs={
        'td': {
            'id': lambda value, record: f"id_{record.id}_status"
        }
    })

    def render_logs(self, value, record):
        """
        Render logs
        """
        if record.status != core_models.EmailBatchMessage.Status.FINISHED:
            url = reverse("core:email_log", kwargs={"pk": record.id})
            return format_html("<a href={}> <i class='bi bi-pencil-square'></i> </a>", url)
        else:
            return "---"

    class Meta:
        """ Meta class"""
        model = core_models.EmailBatchMessage
        attrs = {"class": "table table-striped table-hover",
                 "id": "id_email_batch"}
        template_name = "django_tables2/bootstrap-responsive.html"
        fields = ('edit', 'id', 'role', 'subject', 'date_created', 'date_finished',
                  'total', 'sent', 'sender', 'status', 'logs')
        order_by = ('-date_created')


class EmailBatchRecipientTable(tables.Table):
    """
    Email batch recipient table
    """

    user__email = tables.Column()

    class Meta:
        """ Meta class"""
        model = core_models.EmailBatchRecipient
        attrs = {"class": "table table-striped table-hover"}
        template_name = "django_tables2/bootstrap-responsive.html"
        fields = ('email_batch__pk', 'email_batch__subject',
                  'user__email', 'sent', 'error_message')
        order_by = ('-date_created')


class WorkflowTaskTable(tables.Table):
    """
    Workflow task table
    """

    edit = tables.TemplateColumn(
        verbose_name='',
        template_code='''
        {% if not record.verified %}
            <a href='{% url record.form_view record.register_id  %}?next={% url "core:task_list" %}'> <i class='bi bi-pencil-square'></i></a>
        {% else %}
        <i class='bi bi-pencil-square text-muted'></i>
        {% endif %}
        '''
    )

    class Meta:
        """
        Meta class
        """
        model = core_models.WorkflowTask
        attrs = {"class": "table table-striped table-hover"}
        template_name = "django_tables2/bootstrap-responsive.html"
        fields = ['id', 'edit',  'name', 'status', 'date_created',
                  'operator', 'evaluator', 'date_verified']
        order_by = ('-id')


class CompanyTable(tables.Table):
    """
    Email batch recipient table
    """

    edit = tables.TemplateColumn(
        verbose_name='',
        template_code="<a href='{% url \"core:company_update\" record.id  %}'> <i class='bi bi-pencil-square'></i> </a>"
    )

    class Meta:
        """ Meta class"""
        model = core_models.Company
        attrs = {"class": "table table-striped table-hover"}
        template_name = "django_tables2/bootstrap-responsive.html"
        fields = ['edit', 'name', 'cnpj', 'bank_name',
                  'bank_branch_number', 'bank_branch_digit', 'account_number', 'account_digit']
        order_by = ('-id')


class FAQConfigTable(tables.Table):
    """
    FAQ config table
    """

    edit = tables.TemplateColumn(
        verbose_name='',
        template_code="<a href='{% url \"core:faq_config_update\" record.id  %}'>"
                      "<i class='bi bi-pencil-square'></i></a>"
    )

    class Meta:
        """ Meta class"""
        model = core_models.FAQConfig
        attrs = {"class": "table table-striped table-hover"}
        template_name = "django_tables2/bootstrap-responsive.html"
        fields = ['edit', 'title', 'target_page']


class FAQTable(tables.Table):
    """
    FAQ table
    """

    edit = tables.TemplateColumn(
        verbose_name='',
        template_code="<a href='{% url \"core:faq_update\" record.id  %}'>"
                      "<i class='bi bi-pencil-square'></i></a>"
    )

    class Meta:
        """ Meta class"""
        model = core_models.FAQ
        attrs = {"class": "table table-striped table-hover"}
        template_name = "django_tables2/bootstrap-responsive.html"
        fields = ['edit', 'order', 'question', 'faq_config']
        order_by = ['order']


class StartPageTable(tables.Table):
    """
    Email batch recipient table
    """

    edit = tables.TemplateColumn(
        verbose_name='',
        template_code="<a href='{% url \"core:start_page_update\" record.id  %}'> <i class='bi bi-pencil-square'></i> </a>"
    )

    contact_email = tables.Column()
    support_email = tables.Column()

    site_name = tables.Column(verbose_name='Nome do site', empty_values=())

    class Meta:
        """ Meta class"""
        model = core_models.Company
        attrs = {"class": "table table-striped table-hover"}
        template_name = "django_tables2/bootstrap-responsive.html"
        fields = ['edit', 'site_name', 'contact_email',
                  'support_email', 'support_phone']
        order_by = ('-id')

    def render_site_name(self, value):
        """
        Render site name registered in site model
        """
        try:
            site = Site.objects.get_current()
            return site.name if site else '-----'
        except ImproperlyConfigured:
            return '-----'
