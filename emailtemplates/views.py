"""
    EmailTemplate views
"""

from django.http import HttpResponseRedirect
from django.urls import reverse_lazy

from common.messages import message_add
from common.views import generic, mixins


from . import forms, tables
from .models import EmailTemplate


class EmailTemplateListView(mixins.AdminMixin,
                            mixins.ListViewMixin):
    """
    Email template list
    """
    model = EmailTemplate
    table_class = tables.EmplateTemplateTable
    template_name = 'common/list.html'
    title = 'Modelos de email'
    controls = [
        {'link': {'text': 'Novo', 'url': 'emailtemplate:emailtemplate_create'}},
    ]


class EmailTemplateCreateView(mixins.AdminMixin,
                              generic.CreateView):
    """
    Create email template
    """
    model = EmailTemplate
    form_class = forms.EmailTemplateForm
    template_name = 'common/form.html'
    title = 'Modelo de email'
    success_url = reverse_lazy('emailtemplate:emailtemplate_list')
    cancel_url = success_url


class EmailTemplateUpdateView(mixins.AdminMixin,
                              generic.UpdateView):
    """
    Update email template
    """
    model = EmailTemplate
    form_class = forms.EmailTemplateForm
    template_name = 'common/form.html'
    title = 'Modelo de email'
    success_url = reverse_lazy('emailtemplate:emailtemplate_list')
    cancel_url = success_url

    def form_valid(self, form):
        button = self.request.POST.get('button', None)
        if button == 'delete':
            forms.remove_template(self.object)
            self.object.delete()
            message_add(self.request, "Template removido com sucesso")
            return HttpResponseRedirect(self.get_success_url())
        else:
            return super().form_valid(form)

    def get_controls(self):
        """
        Inserti delete button
        """
        controls = super().get_controls()
        controls.insert(1, mixins.ControlFactory.delete_button())
        return controls
