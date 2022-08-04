"""
    Agreement views
"""
from django.urls import reverse_lazy

from common.views import generic, mixins


from core.models import AcceptanceTerm
from core.forms.core import AccepanceTermForm

from .. import tables


class AcceptanceTermListView(mixins.AdminMixin,
                             mixins.ListViewMixin):
    """
    Acceptance terms list
    """
    model = AcceptanceTerm
    table_class = tables.AcceptanceTable
    template_name = 'common/list.html'
    title = 'Termos de aceite'
    controls = [
        {'link': {'text': 'Novo', 'url': 'core:acceptance_term_create'}},
    ]

    def get_queryset(self):
        return super().get_queryset().order_by('type', '-version')


class AcceptanceTermCreateView(mixins.AdminMixin,
                               generic.CreateView):
    """
    Create acceptance term
    """
    model = AcceptanceTerm
    form_class = AccepanceTermForm
    template_name = 'common/form.html'
    title = 'Termo de aceite'
    success_url = reverse_lazy('core:acceptance_term_list')
    cancel_url = success_url


class AcceptanceTermUpdateView(mixins.AdminMixin,
                               generic.UpdateView):
    """
    Update agreement
    """
    model = AcceptanceTerm
    form_class = AccepanceTermForm
    template_name = 'common/form.html'
    title = 'Termo de aceite'
    success_url = reverse_lazy('core:acceptance_term_list')
    cancel_url = success_url
