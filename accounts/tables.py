"""
    Module for tables
"""

from django.db.models import F
import django_tables2 as tables

from accounts.invitations import Invitation


class InvitationTable(tables.Table):
    """
    Invitation table
    """

    edit = tables.TemplateColumn(
        verbose_name='',
        template_code="<a href='{% url \"invitations:invitation_update\" record.id  %}'> <i class='bi bi-pencil-square'></i> </a>")
    inviter = tables.Column(verbose_name='Remetente')
    accepted = tables.BooleanColumn(verbose_name='Aceito')
    created = tables.DateTimeColumn(verbose_name='Criação', format='d/m/Y H:i')
    sent = tables.DateTimeColumn(verbose_name='Envio', format='d/m/Y H:i')
    expiration_date = tables.DateTimeColumn(format='d/m/Y H:i')
    status = tables.Column(verbose_name='Situação', empty_values=())

    class Meta:
        """
        Meta class
        """
        model = Invitation
        template_name = "django_tables2/bootstrap-responsive.html"
        fields = ['edit',  'email', 'role', 'inviter',
                  'sent', 'created', 'accepted', 'expiration_date', 'status']

        order_by = ('-sent')

    def render_status(self, value, record):
        """
        Render email sending status
        """
        if record.sent:
            return 'Enviado'
        else:
            if record.error_message:
                return record.error_message
            else:
                return 'Agendado para envio'

    def order_sent(self, queryset, is_descending):
        """
        Sent column descend ordering
        """
        if is_descending:
            return (queryset.order_by(F('sent').desc(nulls_first=True)), True)
        else:
            return (queryset.order_by(F('sent').asc(nulls_first=True)), True)


class ApiAccessTable(tables.Table):
    """
    Invitation table
    """

    edit = tables.TemplateColumn(
        verbose_name='',
        template_code="<a href='{% url \"accounts:api_access_update\" record.id  %}'> <i class='bi bi-pencil-square'></i> </a>")

    is_active = tables.BooleanColumn()

    class Meta:
        """
        Meta class
        """
        model = Invitation
        template_name = "django_tables2/bootstrap-responsive.html"
        fields = ['edit', 'user.username', 'operator', 'date_created', 'is_active']
