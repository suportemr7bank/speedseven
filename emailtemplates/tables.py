"""
    Module for tables
"""

import django_tables2 as tables
from .models import EmailTemplate


class EmplateTemplateTable(tables.Table):
    """
        Admin table
    """
    _url = '{% url "emailtemplate:emailtemplate_update" record.id  %}'
    edit = tables.TemplateColumn(
        verbose_name='',
        template_code=f"<a href={_url}> <i class='bi bi-pencil-square'></i> </a>"
    )
    saved = tables.BooleanColumn(verbose_name="Salvo", orderable=False)

    class Meta:
        """ Meta class"""
        model = EmailTemplate
        attrs = {"class": "table table-striped table-hover"}
        template_name = "django_tables2/bootstrap-responsive.html"
        fields = ('edit', 'type', 'prefix', 'date_created', 'date_modified', 'saved')

    # pylint: disable=unused-argument
    def render_saved(self, value, record):
        """
        Verify if file exists
        """
        return 'Sim' if not record.write_error else 'Não'
