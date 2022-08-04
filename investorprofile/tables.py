import django_tables2 as tables

from .models import ProfileTest


class ProfileTestTable(tables.Table):
    """
    Agreement table
    """
    edit = tables.TemplateColumn(
        verbose_name='Edição simples',
        template_code="<a href='{% url \"investorprofile:profile_test_update\" record.id  %}'> <i class='bi bi-pencil-square'></i> </a>",
        orderable=False)

    preview = tables.TemplateColumn(
        verbose_name='Visualizar',
        template_code="<a href='{% url \"investorprofile:profile_test_detail\" record.id  %}'> <i class='bi bi-eye'></i> </a>",
        orderable=False)

    id = tables.Column(verbose_name='Número de série')

    class Meta:
        """ Meta class"""
        model = ProfileTest
        attrs = {"class": "table table-striped table-hover"}
        template_name = "django_tables2/bootstrap-responsive.html"
        fields = ('edit', 'preview','id',  'title', 'published', 'is_active')
