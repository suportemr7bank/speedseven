"""
Investment views
"""

from django.urls import reverse_lazy


from common.views import mixins, generic
from common.forms import mixins as form_mixins

from .. import forms, tables
from ..models import ApplicationAccount, ApplicationOp, Application


class ApplicationListView(mixins.AdminMixin, mixins.ListViewMixin):
    """
    Application list
    """
    model = Application
    table_class = tables.ApplicationTable
    template_name = 'common/list.html'
    title = 'Aplicações'
    controls = [
        {'link': {'text': 'Novo', 'url': 'investment:application_create'}},
    ]


class ApplicationCreateView(mixins.AdminMixin, form_mixins.LoggedUserMixin, generic.CreateView):
    """
    Application creation
    """
    model = Application
    form_class = forms.ApplicationForm
    template_name = 'common/form.html'
    title = 'Aplicação'
    cancel_url = reverse_lazy('investment:application_list')

    def get_success_url(self) -> str:
        return reverse_lazy('investment:application_settings', kwargs={'pk': self.object.pk})

    def get_controls(self):
        controls = super().get_controls()
        controls[1].text = 'Salvar e configurar'
        return controls


class ApplicationUpdateView(mixins.AdminMixin, form_mixins.LoggedUserMixin, generic.UpdateView):
    """
    Application update
    """
    model = Application
    form_class = forms.ApplicationForm
    template_name = 'common/form.html'
    title = 'Aplicação'
    success_url = reverse_lazy('investment:application_list')
    cancel_url = success_url


class ApplicationAccountListView(mixins.AdminMixin, mixins.ListViewMixin):
    """
    List of applications
    """
    model = ApplicationAccount
    table_class = tables.ApplicationAccountTable
    template_name = 'common/list.html'
    title = 'Contas'
    controls = [
        {'link': {'text': 'Novo', 'url': 'investment:applicationaccount_create'}},
    ]


class ApplicationAccountCreateView(mixins.AdminMixin,
                                   form_mixins.LoggedUserMixin, generic.CreateView):
    """
    Application model creation
    """
    form_class = forms.ApplicationAccountForm
    template_name = 'common/form.html'
    title = 'Conta'
    success_url = reverse_lazy('investment:applicationaccount_list')
    cancel_url = success_url




class ApplicationOpListView(mixins.AdminMixin, mixins.ListViewMixin):
    """
    List of application operations
    """
    model = ApplicationOp
    table_class = tables.ApplicationOpTable
    template_name = 'common/list.html'
    title = 'Extrato'


class ApplicationOpUserListBaseView(mixins.ListViewMixin):
    """
    List of application operations
    """
    model = ApplicationOp
    table_class = tables.ApplicationOpTable
    template_name = 'common/list.html'
    title = 'Extrato'
