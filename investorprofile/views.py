"""
Profile test form

"""

from django import forms
from django.http import HttpResponseNotAllowed
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView

from common.views import generic, mixins

from . import models, tables
from .forms import create_form_class, ProfileForm
from .models import ProfileTest


class EmptyForm(forms.Form):
    """
    Empty form for profile test if profile test is absent
    """
    pass


class ProfileTestBaseViewMixin:
    """
    Mixin to build profile test view
    """

    def get_profile_test_object(self):
        """
        The profile test object to build form
        """
        #pylint: disable=no-member
        return ProfileTest.objects.filter(is_active=True).last()

    def get_form_class(self):
        """
        Form class built from profile test object model
        """
        obj = self.get_profile_test_object()
        if obj:
            self.form_class = create_form_class(profile_test_obj=obj)
        else:
            self.form_class = EmptyForm
        return self.form_class

    def get_form_kwargs(self):
        """
        Insert user in the form constructor
        """
        kwargs = super().get_form_kwargs()
        if self.form_class != EmptyForm:
            kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        """
        Save profile test
        """
        form.save()
        return super().form_valid(form)


class ProfileTestCreateViewMixin(ProfileTestBaseViewMixin):
    """
    Profile creation
    """

    def get(self, request, *args, **kwargs):
        """
        Forbid creating a new investor profile if at least one was created
        """
        user = self.request.user
        investorprofile = user.investorprofile_set.last()
        if investorprofile:
            return HttpResponseNotAllowed(['GET', 'POST'], content="Method not allowed")
        return super().get(request, *args, **kwargs)


class ProfileTestListView(mixins.AdminMixin,
                          mixins.ListViewMixin):
    """
    Acceptance terms list
    """
    model = ProfileTest
    table_class = tables.ProfileTestTable
    template_name = 'common/list.html'
    title = 'Testes de perfil'
    controls = [
        {'link': {'text': 'Novo', 'url': 'admin:investorprofile_profiletest_add'}},
    ]


class ProfileTestUpdateView(mixins.AdminMixin,
                            generic.UpdateView):
    """
    Update product
    """
    model = models.ProfileTest
    form_class = ProfileForm
    template_name = 'common/form.html'
    title = 'Teste de perfil'
    success_url = reverse_lazy('investorprofile:profile_test_list')
    cancel_url = success_url

    def get_controls(self):
        """
        Insert link to admin change page
        """
        controls = super().get_controls()
        if self.object and not self.object.published:
            url = reverse('admin:investorprofile_profiletest_change',
                        args=(self.object.pk,))
            control = mixins.ControlFactory.link_button(
                'Editar questões', url, color='secondary')
            controls.insert(1, control)
        return controls


class ProfileTestDetailView(mixins.AdminMixin,
                            mixins.ControlMixin,
                            TemplateView):
    """
    Update product
    """
    model = models.ProfileTest
    fields = "__all__"
    template_name = 'investorprofile/form.html'
    fields = ['title', 'description', 'info', 'is_active']
    title = 'Prévia do teste de perfil'
    cancel_url = reverse_lazy('investorprofile:profile_test_list')

    def get_context_data(self, **kwargs):
        # pylint: dislable=no-member
        test = get_object_or_404(ProfileTest, pk=self.kwargs['pk'])
        form = create_form_class(profile_test_obj=test)
        context = super().get_context_data(**kwargs)
        context['form'] = form
        return context

    def get_controls(self):
        controls = super().get_controls()
        controls.pop()
        controls[0].text = 'Fechar'
        controls[0].color = 'secondary'
        return controls
