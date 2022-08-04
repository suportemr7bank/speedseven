"""
Email views
"""

from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.urls import reverse_lazy

from common.views import generic, mixins
from core import models, tables, tasks
from core.forms import email


class EmailListView(mixins.AdminMixin,
                    mixins.WebsockeMixin,
                    mixins.ListViewMixin):
    """
        Admin list
    """
    model = models.EmailBatchMessage
    table_class = tables.EmailBatchTable
    template_name = 'common/list.html'
    title = 'Mensagens'
    socket_name = 'send_batch_email'
    controls = [
        {'link': {'text': 'Novo', 'url': 'core:email_create'}},
    ]


class EmailCreateView(mixins.AdminMixin,
                      generic.CreateView):
    """
    Email create view to send email to user group according to user role
    """
    model = models.EmailBatchMessage
    form_class = email.EmailBatchForm
    template_name = 'common/form.html'
    title = 'Nova mensagem'
    success_url = reverse_lazy('core:email_list')
    cancel_url = success_url

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        return response

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # For some unknown reason, if message readonly is set to True in the
        # update view it must be set to False here
        form.fields['message'].widget.mce_attrs.update({'readonly': False})
        return form

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            tasks.send_email.delay(self.object.pk)
        except Exception as err:
            form.add_error(None, 'Problema ao enviar email em segundo plano.')
            form.add_error(None, str(err))
            response = self.form_invalid(form)
            self.object.delete()

        return response

    def get_controls(self):
        """
        Default form controls list
        """
        controls = super().get_controls()
        controls[1].text = 'Enviar'
        return controls

    def get_success_message(self):
        return "Envio de email agendado"


class EmailUpdateView(mixins.AdminMixin,
                      generic.UpdateView):
    """
    Email update view to send email to user group according to user role
    """
    model = models.EmailBatchMessage
    form_class = email.EmailBatchForm
    template_name = 'common/form.html'
    title = 'Mensagem enviada'
    success_url = reverse_lazy('core:email_list')
    cancel_url = success_url

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        for _key, field in form.fields.items():
            field.disabled = True
        # Set to readonly keeps it state even if the view accessed after this is the
        # create view (for some unknown reason)
        form.fields['message'].widget.mce_attrs.update({'readonly': True})
        return form

    def form_valid(self, form):
        status = models.EmailBatchMessage.Status
        if self.object.status in status.FINISHED:
            return HttpResponseBadRequest('O email não pode ser editado')
        else:
            tasks.send_email.delay(self.object.pk)
            return HttpResponseRedirect(self.success_url)

    def get_controls(self):
        "Only cancel button is kept"
        controls = super().get_controls()
        controls.pop(1)
        status = models.EmailBatchMessage.Status
        if self.object.status in status.FINISHED:
            controls.pop(1)
        elif self.object.status == status.FINISHED_ERR:
            controls[1].text = "Reenviar (apenas falhos)"
        elif self.object.status in [status.PROCESSING, status.WAITING]:
            controls[1].text = "Reenviar (apenas não enviados)"

        return controls


class EmailLogView(mixins.AdminMixin,
                   mixins.ListViewMixin):
    """
        Admin list
    """
    model = models.EmailBatchRecipient
    table_class = tables.EmailBatchRecipientTable
    template_name = 'common/list.html'
    title = 'Log de mensagens'
    socket_name = 'send_batch_email'

    def get_queryset(self):
        return super().get_queryset().filter(email_batch=self.kwargs['pk'])
