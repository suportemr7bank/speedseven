"""
Investment views
"""

from django.urls import reverse_lazy
from common.views import generic, mixins
from common.forms import mixins as form_mixins

from .. import forms, tables
from ..models import ApplicationModel


class ApplicationModelListView(mixins.AdminMixin, mixins.ListViewMixin):
    """
    Application model list
    """
    model = ApplicationModel
    table_class = tables.ApplicationModelTable
    template_name = 'common/list.html'
    title = 'Modelos de aplicação'
    controls = [
        {'link': {'text': 'Novo', 'url': 'investment:applicationmodel_create'}},
    ]


class ApplicationModelCreateView(mixins.AdminMixin,
                                 form_mixins.LoggedUserMixin, generic.CreateView):
    """
    Application model creation
    """
    model = ApplicationModel
    form_class = forms.ApplicationModelForm
    template_name = 'common/form.html'
    title = 'Modelo de aplicação'
    success_url = reverse_lazy('investment:applicationmodel_list')
    cancel_url = success_url


class ApplicationModelUpdateView(mixins.AdminMixin,
                                 form_mixins.LoggedUserMixin, generic.UpdateView):
    """
    Application model update
    """
    model = ApplicationModel
    form_class = forms.ApplicationModelForm
    template_name = 'common/form.html'
    title = 'Modelo de aplicação'
    success_url = reverse_lazy('investment:applicationmodel_list')
    cancel_url = success_url
