
"""
Faq views
"""

from django.urls import reverse_lazy
from common.views import mixins, generic
from core import tables, models
from core.forms.faq import FAQForm


class FAQConfigListView(mixins.AdminMixin,
                        mixins.ListViewMixin):
    """
    FAQ config list view
    """
    model = models.FAQConfig
    template_name = 'common/list.html'
    title = 'Páginas de ajuda'
    table_class = tables.FAQConfigTable

    controls = [
        {'link': {'text': 'Novo', 'url': 'core:faq_config_create'}},
    ]


class FAQConfigCreateView(mixins.AdminMixin,
                          generic.CreateView):
    """
    FAQ config create view
    """
    model = models.FAQConfig
    fields = '__all__'
    template_name = 'common/form.html'
    title = 'Página de ajuda'
    success_url = reverse_lazy('core:faq_config_list')
    cancel_url = success_url


class FAQConfigUpdateView(mixins.AdminMixin,
                          generic.UpdateView):
    """
    FAQ config update view
    """
    model = models.FAQConfig
    fields = '__all__'
    template_name = 'common/form.html'
    title = 'Página de ajuda'
    success_url = reverse_lazy('core:faq_config_list')
    cancel_url = success_url


class FAQListView(mixins.AdminMixin,
                  mixins.ListViewMixin):
    """
    FAQ list view
    """
    model = models.FAQ
    template_name = 'common/list.html'
    title = 'Questões frequentes'

    table_class = tables.FAQTable

    controls = [
        {'link': {'text': 'Novo', 'url': 'core:faq_create'}},
    ]


class FAQCreateView(mixins.AdminMixin,
                    generic.CreateView):
    """
    FAQ create view
    """
    model = models.FAQ
    form_class = FAQForm
    template_name = 'common/form.html'
    title = 'Nova questão'
    success_url = reverse_lazy('core:faq_list')
    cancel_url = success_url


class FAQUpdateView(mixins.AdminMixin,
                    generic.UpdateView):
    """
    FAQ update view
    """
    model = models.FAQ
    form_class = FAQForm
    template_name = 'common/form.html'
    title = 'Questão'
    success_url = reverse_lazy('core:faq_list')
    cancel_url = success_url
    enable_delete = True
    confirm_operation = 'delete'
