"""
    Views adapted from django and helper mixins
"""


import extra_views
from django.http import (FileResponse, HttpResponseForbidden,
                         HttpResponseNotFound, HttpResponseRedirect)
from django.views import generic

from common.forms.helper import FormSetHelper
from common.messages import message_add
from common.views import mixins

from .mixins import ControlFactory, ControlMixin


class CreateView(ControlMixin, generic.CreateView):
    """
    Extends create view to include form title
    """

    def form_valid(self, form):
        message_add(self.request, self.get_success_message())
        return super().form_valid(form)

    def get_success_message(self):
        """
        Message when data are saved
        """
        return "Dados salvos com sucesso"


class UpdateView(ControlMixin, generic.UpdateView):
    """
    Extends update view to include form title
    """

    success_message = "Dados atualizados com sucesso"
    enable_delete = False

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if self.enable_delete and self.request.POST.get('button', None)=='delete':
            return self.delete()
        return response

    def delete(self):
        """
        Delete request
        """
        obj = self.get_object()
        success_url = self.get_success_url()
        obj.delete()
        return HttpResponseRedirect(success_url)

    def form_valid(self, form):
        message_add(self.request, self.success_message)
        if getattr(self, 'success_url'):
            if next_url := self.request.GET.get('next', None):
                self.success_url = next_url
        return super().form_valid(form)

    def get_controls(self):
        """
            Default form controls list
        """
        controls = [
            ControlFactory.cancel_button(self.cancel_url),
            ControlFactory.save_continue_button(),
            ControlFactory.save_button(),
        ]

        if self.enable_delete:
            controls.insert(1, ControlFactory.delete_button())

        return controls


class FormView(ControlMixin, generic.FormView):
    """
    Extends create view to include form title
    """


class PrintView(mixins.TitleMixin, generic.DetailView):
    """
    Extends detail view to include form title
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['content'] = self.get_content()
        return context

    def get_content(self):
        """
        {'title': <title>, 'text': <text>}
        """
        return dict()


class CreateWitthInlinesView(ControlMixin, extra_views.CreateWithInlinesView):
    """
    Extends create view to include form title
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['formset_helper'] = FormSetHelper()
        return context

    def form_valid(self, form):
        message_add(self.request, "Dados salvos com sucesso")
        return super().form_valid(form)


class UpdateWitthInlinesView(ControlMixin, extra_views.UpdateWithInlinesView):
    """
    Extends create view to include form title
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['formset_helper'] = FormSetHelper()
        return context

    def form_valid(self, form):
        message_add(self.request, "Dados salvos com sucesso")
        return super().form_valid(form)


class FileBaseView(generic.View):
    """
    Base view for private media file downloading
    """

    model = None
    field = None
    media_file_root = None

    # pylint: disable=unused-argument
    def get(self, request, *args, **kwargs):
        """
        Return file or file not found
        """
        if self.can_access_file(request):
            file_name = kwargs.get('file_name')
            # pylint: disable=assignment-from-none
            file = self.get_file_obj(file_name, request)
            if file:
                try:
                    return FileResponse(file)
                except FileNotFoundError:
                    pass
            return HttpResponseNotFound('Arquivo não encontrado')
        return HttpResponseForbidden('Acesso não peritido')

    def get_file_obj(self, file_name, request):
        """
        File object to file_name and user
        """
        query = self.queryset(file_name, request)

        if query.count() == 1:
            return getattr(query.first(), self.field)
        return None

    def queryset(self, file_name, request):
        """
        Queryset
        """
        data = {
            f'{self.field}__exact': f'{self.media_file_root}{file_name}'
        }

        query = self.model.objects.filter(**data)
        return query

    def can_access_file(self, request):
        """
        Allow control access to file
        """
        return True
