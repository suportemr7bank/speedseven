"""
View mixins
"""

from dataclasses import dataclass
from http import HTTPStatus

from django.http import HttpResponseRedirect
from django_tables2 import SingleTableView

from accounts.auth import mixins as auth_mixins
from core import websocket


class PageMenuMixin:
    """
    Mixin to include page menu
    """
    menu_template_name = None

    def get_context_data(self, **kwargs):
        """
        Include menu template in the context
        """
        context = super().get_context_data(**kwargs)
        context['menu_template'] = self.menu_template_name
        return context


class TitleMixin:
    """
    Mixin to include title to template
    """
    title = ''
    header_message = ''

    def get_context_data(self, **kwargs):
        """
        Inclue title in context
        """
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        context['header_message'] = self.header_message
        return context


@dataclass
class Control:
    """
    Buttons to control forms
    """
    control_type: str
    name: str
    value: str
    text: str
    # primary, success, danger
    color: str = 'success'


class ControlFactory:
    """
    Create standard controls
    """

    @classmethod
    def button(cls, value, text, color):
        """
        Create link button
        """
        return Control('button', 'button', value, text, color)

    @classmethod
    def link_button(cls, label, url, color):
        """
        Create link button
        """
        return Control('link', 'link', url, label, color)

    @classmethod
    def save_button(cls, text='Salvar'):
        """
        Default save button
        """
        return cls.button('save', text, 'success')

    @classmethod
    def save_continue_button(cls):
        """
        Default save and continue button
        """
        return cls.button('save_continue', 'Salvar e continuar', 'success')

    @classmethod
    def delete_button(cls):
        """
        Default delete button
        """
        return cls.button('delete', 'Apagar', 'danger')

    @classmethod
    def cancel_button(cls, redirect_url):
        """
        Default cancel button
        """
        return cls.link_button('Cancelar', redirect_url, 'danger')


class ControlMixin(TitleMixin):
    """
    Mixin to hadle control (cancel and save butttons)
    Used with common/forms.html
    """
    cancel_url = None
    confirm_operation = None

    def get_context_data(self, **kwargs):
        """
        Inclue control in context
        Handle save and cancel buttons
        """
        context = super().get_context_data(**kwargs)
        context['controls'] = self.get_controls()
        context['cancel_url'] = self.cancel_url
        context['confirm_operation'] = self.confirm_operation
        return context

    def get_controls(self):
        """
        Default form controls list
        """
        return [
            ControlFactory.cancel_button(self.cancel_url),
            ControlFactory.save_button()
        ]

    def post(self, request, *args, **kwargs):
        """
        Customize post to include save and continue
        Usage: create a button with name="button" value="save_continue" in html file
        """
        response = super().post(request, *args, **kwargs)
        redirect = self.after_post_redirect(request, response)
        if redirect:
            return redirect
        return response

    def after_post_redirect(self, request, response):
        """
        Redirect behaviour according submit button can be changed here
        """
        button = self.request.POST.get('button')
        if response.status_code == HTTPStatus.FOUND and button == 'save_continue':
            return HttpResponseRedirect(redirect_to=request.path_info)
        return None


class ListViewMixin(TitleMixin, SingleTableView):
    """
    Mixin for list (tables views)
    Defines a control and a table for view
    template_name must be defined
    """
    controls = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['controls'] = self.controls
        return context


class AdminMixin(auth_mixins.LoginRequiredMixin,
                 auth_mixins.PermissionRequiredMixin,
                 PageMenuMixin):
    """
    Mixin to add admin menu to template
    """

    permission_required = 'is_admin'
    menu_template_name = 'core/menu.html'


class WebsockeMixin:
    """
    Mixin to load websocket
    """
    socket_name = None

    def get_context_data(self, **kwargs):
        """
        Context with socket_name
        """
        context = super().get_context_data(**kwargs)
        if self._socket_available():
            context['socket_name'] = {'socket_name': self.socket_name}
        else:
            context['socket_name'] = {'socket_name': None}
        return context

    def _socket_available(self):
        """
        Test if websocke broker service is available
        """
        return websocket.is_websocket_available()
