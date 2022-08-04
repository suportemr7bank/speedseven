"""
    Core adminitrative view
"""

import os
from django.conf import settings
from django.contrib.auth import forms as auth_forms
from django.http import FileResponse, Http404, HttpResponseNotFound, HttpResponseRedirect, JsonResponse
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, View
from drf_spectacular.views import SpectacularAPIView as _SpectacularAPIView
from drf_spectacular.views import SpectacularRedocView as _SpectacularRedocView
from drf_spectacular.views import \
    SpectacularSwaggerView as _SpectacularSwaggerView

from accounts import roles as account_roles
from accounts.auth import mixins as auth_mixins
from clients import forms as clients_forms
from clients import models as clients_models
from common.forms import mixins as forms_mixins
from common.messages import message_add
from common.views import generic, mixins
from investorprofile import models as invprof_models
from products import models as products_models

from core import models as core_models
from core import workflow

from .. import tables
from ..forms import core


class StartView(mixins.AdminMixin, TemplateView):
    """
        Admin start view
    """
    template_name = 'core/start.html'

    def get_context_data(self, **kwargs):
        # pylint: disable=no-member

        context = super().get_context_data(**kwargs)

        context['account_term'] = core_models.AcceptanceTerm.objects.filter(
            type=core_models.AcceptanceTerm.Type.PRIVACY_POLICY).exists()
        context['signup_term'] = core_models.AcceptanceTerm.objects.filter(
            type=core_models.AcceptanceTerm.Type.SIGNUP).exists()

        count_prod = products_models.Product.objects.all().count()
        context['products_num'] = count_prod
        context['agreements_num'] = count_prod - \
            products_models.Product.objects.filter(
                agreementtemplate__isnull=True).count()

        context['invprof_num'] = invprof_models.Profile.objects.all().count()

        context['has_profile_test'] = invprof_models.ProfileTest.objects.filter(
            is_active=True).exists()

        context['dashboards_num'] = count_prod - \
            products_models.Product.objects.filter(
                productdashboard__isnull=True).count()

        return context


class AdminListView(mixins.AdminMixin,
                    forms_mixins.UserNameEmailFilterMixin,
                    mixins.ListViewMixin):
    """
        Admin list
    """
    model = core_models.User
    table_class = tables.AdminTable
    template_name = 'common/list.html'
    title = 'Administradores'

    def get_queryset(self):
        return super().get_queryset().filter(is_superuser=True)


class ChangeUserPasswordView(mixins.AdminMixin,
                             generic.FormView):
    """
    Change user password
    """
    form_class = auth_forms.SetPasswordForm
    success_url = reverse_lazy('core:user_list')
    template_name = 'common/form.html'
    title = "Alterar senha"
    cancel_url = success_url

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        user_id = self.kwargs['pk']
        try:
            user = core_models.User.objects.get(pk=user_id)
            kwargs['user'] = user

            self.header_message = user.email
        # pylint: disable=no-member
        except core_models.User.DoesNotExist as ex:
            kwargs['user'] = None
            # TODO: redirecionar para página de erro
            raise ex
        return kwargs

    def form_valid(self, form):
        # From is not automatically saved
        form.save()
        message_add(self.request, 'Senha alterada com sucesso!')
        return super().form_valid(form)


class ChangeAdminPasswordView(ChangeUserPasswordView):
    """
    Change asmin password
    """
    success_url = reverse_lazy('core:admin_list')
    cancel_url = success_url
    form_class = auth_forms.PasswordChangeForm

    def _check_user(self, request, kwargs):
        """
        Asserts only logged user can change his/her password
        """
        try:
            user_id = kwargs['pk']
            user = core_models.User.objects.get(pk=user_id)
            if user != request.user:
                #TODO: customize
                return False
        # pylint: disable=no-member
        except core_models.User.DoesNotExist:
            return False

        return True

    def get(self, request, *args, **kwargs):
        if not self._check_user(request, kwargs):
            raise Http404
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not self._check_user(request, kwargs):
            raise Http404
        return super().post(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        user_id = self.kwargs['pk']
        try:
            user = core_models.User.objects.get(pk=user_id)
            kwargs['user'] = user

            message = (
                '<span class="text-danger">Atençao!</span>'
                ' Será feito logout automático após mudança de senha'
            )

            self.header_message = f'<p>{user.email}</p> {message}'
        #pylint: disable=no-member
        except core_models.User.DoesNotExist as ex:
            kwargs['user'] = None
            # TODO: redirecionar para página de erro
            raise ex
        return kwargs


class ChangePasswordMixin:
    """
    Insert a button to change password
    """

    def get_password_url(self):
        """
        Url for changing password
        """
        return ''

    def get_controls(self):
        """
        Insert a button to change password
        """
        controls = super().get_controls()
        url = self.get_password_url()
        if url:
            controls.insert(
                1,
                mixins.ControlFactory.link_button(
                    'Alterar senha', url, 'secondary'),
            )

        return controls


class AdminUpdateView(mixins.AdminMixin,
                      ChangePasswordMixin,
                      generic.UpdateView):
    """
        Create admin
    """
    model = core_models.User
    form_class = core.AdminForm
    template_name = 'common/form.html'
    title = 'Administradores'
    success_url = reverse_lazy('core:admin_list')
    cancel_url = success_url

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_password_url(self):
        if self.object.pk == self.request.user.pk:
            return reverse('core:change_admin_password', kwargs={'pk': self.object.pk})
        return None


class UserListView(mixins.AdminMixin,
                   forms_mixins.UserNameEmailFilterMixin,
                   mixins.ListViewMixin):
    """
        Admin list
    """
    model = core_models.User
    table_class = tables.UserTable
    template_name = 'common/list.html'
    title = 'Ativação e senha'

    def get_queryset(self):
        return super().get_queryset(
        ).filter(
            is_superuser=False
        ).exclude(
            userrole__role=account_roles.Roles.APIAPP
        ).order_by('-id')


class UserUpdateView(mixins.AdminMixin,
                     ChangePasswordMixin,
                     generic.UpdateView):
    """
    Update user
    """
    model = core_models.User
    form_class = core.UserActivationForm
    template_name = 'common/form.html'
    title = 'Ativação e senha'
    success_url = reverse_lazy('core:user_list')
    cancel_url = success_url

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_password_url(self):
        return reverse('core:change_user_password', kwargs={'pk': self.object.pk})


class ClientListView(mixins.AdminMixin,
                     forms_mixins.UserNameEmailFilterMixin,
                     mixins.ListViewMixin):
    """
        Admin list
    """
    model = clients_models.Client
    table_class = tables.ClientsTable
    template_name = 'common/list.html'
    title = 'Clientes'
    controls = [
        {'link': {'text': 'Novo', 'url': 'core:client_create'}},
    ]


class ClientCreateView(mixins.AdminMixin,
                       workflow.ApprovalWorkflowViewMixin,
                       generic.CreateView):
    """
        Update client
        Client is creates by signal when user signed up
    """
    model = clients_models.Client
    form_class = clients_forms.ClientCreateForm
    template_name = 'common/form.html'
    title = 'Dados pessoais'
    success_url = reverse_lazy('core:client_list')
    cancel_url = success_url
    skip_signup_test = True

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['operator'] = self.request.user
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        cleaned_data = form.cleaned_data
        if cleaned_data['next_step'] == clients_forms.ClientCreateForm.NEXT_STEP_INSERT:
            return HttpResponseRedirect(
                reverse('core:client_update', kwargs={'pk': form.instance.pk})
            )
        return response


class ClientUpdateView(mixins.AdminMixin,
                       workflow.ApprovalWorkflowViewMixin,
                       generic.UpdateView):
    """
        Update client
        Client is creates by signal when user signed up
    """
    model = clients_models.Client
    form_class = clients_forms.ClientForm
    template_name = 'common/form.html'
    title = 'Dados pessoais'
    success_url = reverse_lazy('core:client_list')
    cancel_url = success_url
    skip_signup_test = True

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.object.user
        kwargs['operator'] = self.request.user
        return kwargs


class ApiUserView(auth_mixins.RoleMixin, mixins.PageMenuMixin,  TemplateView):
    """
    View to api user
    """

    role = account_roles.Roles.APIACC
    menu_template_name = 'core/api_user_menu.html'
    template_name = 'core/api_user_start.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['api_production_mode'] = settings.API_ENABLE_PRODUCTION_MODE
        return context


class SpectacularAPIView(auth_mixins.RoleMixin, _SpectacularAPIView):
    """
    SpectacularAPIView
    """
    role = account_roles.Roles.APIACC


class SpectacularRedocView(auth_mixins.RoleMixin, _SpectacularRedocView):
    """
    SpectacularRedocView
    """
    role = account_roles.Roles.APIACC


class SpectacularSwaggerView(auth_mixins.RoleMixin, _SpectacularSwaggerView):
    """
    SpectacularSwaggerView
    """
    role = account_roles.Roles.APIACC


class WorkflowTaskListView(mixins.AdminMixin,
                           mixins.ListViewMixin):
    """
    Workflow task view
    """
    model = core_models.WorkflowTask
    table_class = tables.WorkflowTaskTable
    template_name = 'common/list.html'
    title = 'Aprovação de cadastros'


class CompanyListView(mixins.AdminMixin,
                      mixins.ListViewMixin):
    """
    Company list
    """
    model = core_models.Company
    table_class = tables.CompanyTable
    template_name = 'common/list.html'
    title = 'Dados da empresa'
    controls = [
        {'link': {'text': 'Criar', 'url': 'core:company_create'}},
    ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object_list.count() > 0:
            context.pop('controls')
        return context


class CompanyCreateView(mixins.AdminMixin,
                        generic.CreateView):
    """
    Create company
    """
    model = core_models.Company
    form_class = core.CompanyForm
    template_name = 'common/form.html'
    title = 'Dados da empresa'
    success_url = reverse_lazy('core:company_list')
    cancel_url = success_url


class CompanyUpdateView(mixins.AdminMixin,
                        generic.UpdateView):
    """
    Update company
    """
    model = core_models.Company
    form_class = core.CompanyForm
    template_name = 'common/form.html'
    title = 'Dados da empresa'
    success_url = reverse_lazy('core:company_list')
    cancel_url = success_url


@method_decorator(csrf_exempt, name='dispatch')
class TinyMceUploadView(auth_mixins.LoginRequiredMixin,
                        auth_mixins.PermissionRequiredMixin,
                        View):
    """
    View to upload tinymce rich text field images
    """
    permission_required = 'is_admin'

    def post(self, request, *args, **kwargs):
        """
        Handle post method
        """

        file_obj = request.FILES['file']
        file_name_suffix = file_obj.name.split(".")[-1]
        if file_name_suffix not in ["jpg", "png", "gif", "jpeg", ]:
            return JsonResponse({"message": "Wrong file format"})

        path = settings.TINYMCE_UPLOAD_FOLDER

        # If there is no such path, create
        if not os.path.exists(path):
            os.makedirs(path)

        date = timezone.localtime(timezone.now()).strftime('%Y%m%d-%H%M%S')

        file_name = f'{date}_{file_obj.name}'

        file_path = os.path.join(path, file_name)

        file_url = f'{settings.TINYMCE_URL}{file_name}'

        if os.path.exists(file_path):
            return JsonResponse({
                "message": "file already exist",
                'location': file_url
            })

        with open(file_path, 'wb+') as f:
            for chunk in file_obj.chunks():
                f.write(chunk)

        return JsonResponse({
            'message': 'Image uploaded successfully',
            'location': file_url
        })


class TinyMceDocView(View):
    """
    View doc files
    """

    def get(self, request, *args, **kwargs):
        """
        Handle image file request
        """

        file_path = os.path.join(
            settings.TINYMCE_UPLOAD_FOLDER, kwargs.get('file_name'))

        try:
            img = open(file_path, 'rb')
            return FileResponse(img)
        except FileNotFoundError:
            return HttpResponseNotFound()
