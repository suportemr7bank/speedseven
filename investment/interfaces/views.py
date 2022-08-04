
"""
Views to applications created from application models
Each application have it's forms and methods according to intestiment interface
Application implementation is in investment.appication as django apps
"""

from django import forms
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404

from common.views import mixins, generic
from core.models import Company

from ..models import Application, ApplicationAccount, MoneyTransfer
from .enums import ApplicationFormType


class EmptyForm(forms.Form):
    """
    Empty form for when there is no form to be loaded
    """

    def __init__(self, *args, **kwargs):
        kwargs.pop('instance')
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        """ Does nothing """


class FormLoaderMixin:
    """
    Load form class depending on application
    """

    application_form = None

    def __init__(self) -> None:
        super().__init__()
        self.has_form = False
        self.user = None
        self.application = None
        self.app_class = None
        self.form = None

    def dispatch(self, request, *args, **kwargs):
        """
        View dispatch melhod
        """
        # pylint: disable=no-member
        self.user = request.user
        # pylint: disable=assignment-from-none
        self.application = self.get_application()
        self.app_class = self.application.application_class
        # pylint: disable=protected-access
        application_account = getattr(self, 'application_account', None)
        self.form = self.app_class.get_form(self.application_form, application_account)
        if self.form and getattr(self.form, '_meta', None):
            self.queryset = self.form._meta.model.objects.all()
        return super().dispatch(request, *args, **kwargs)

    def get_form_class(self):
        """
        Load form class
        """
        if self.app_class:
            if self.form:
                if self.user.is_superuser:
                    if product:=getattr(self.application, 'product', None):
                        self.header_message = f'Aplicação - {self.application.display_text} <br> Produto associado - {product.display_text}'
                    else:
                        self.header_message = f'Aplicação - {self.application.display_text} <br> Aplicação sem produto associado'
                else:
                    self.header_message = self.application.product.display_text

                self.has_form = True
                return self.form
            else:
                self.header_message = 'Operação indisponível'
        else:
            self.header_message = 'Aplicação indisponível indisponível'
        return EmptyForm

    def get_form_kwargs(self):
        """
        Insert user to form kwargs
        """
        kwargs = super().get_form_kwargs()
        if self.has_form:
            kwargs['user'] = self.user
        return kwargs

    def get_application(self):
        """
        Load app_class
        """
        return None

    def get_controls(self):
        """
        Remove save if form is null
        """
        controls = super().get_controls()
        if not self.form:
            del controls[1]
        return controls


class ApplicationBaseView(mixins.AdminMixin, FormLoaderMixin, generic.UpdateView):
    """
    Base view for applications
    """

    template_name = 'common/form.html'
    success_message = None

    def __init__(self) -> None:
        super().__init__()
        self.application = None
        self.user = None

    def get_application(self):
        # pylint: disable=no-member
        return get_object_or_404(Application, pk=self.kwargs['pk'])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if not self.has_form:
            del kwargs['instance']
        if self.has_form:
            kwargs['application'] = self.application
        return kwargs

    def get_object(self, queryset=None):
        pass


class ApplicationSettingsBaseView(ApplicationBaseView):
    """
    Base view for applications
    """

    template_name = 'common/form.html'
    success_message = None

    def __init__(self) -> None:
        super().__init__()
        self.application = None
        self.user = None

    def get_object(self, queryset=None):
        # The pk passed to the view belongs to application object,
        # used only to load correct application model class.
        # This return the correct objet according to the accont settings model
        # define in the application model class.
        return self.application.settings


class ApplicationSettingsView(ApplicationSettingsBaseView):
    """
    Settings for application created fom application model
    """

    success_url = reverse_lazy('investment:application_list')
    template_name = 'common/form.html'
    cancel_url = success_url
    success_message = 'Configurações salvas com sucesso!'
    title = 'Configuração da aplicação'
    application_form = ApplicationFormType.APPLICATION_SETTINGS


class ApplicationAccountBaseView(FormLoaderMixin):
    """
    Application base for client account
    """
    success_url = reverse_lazy('investment:moneytransfer_list')
    application_account = None

    def __init__(self) -> None:
        super().__init__()
        self.application_account = None

    def dispatch(self, request, *args, **kwargs):
        # pylint: disable=no-member
        self.application_account = self.get_application_account(kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_application_account(self, object_pk):
        """
        Application account
        """
        # pylint: disable=no-member
        self.application_account = ApplicationAccount.objects.get(pk=object_pk)
        return self.application_account

    def get_application(self):
        return self.application_account.application

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # pylint: disable=no-member
        if self.has_form:
            kwargs['application_account'] = self.application_account
        return kwargs


class ApplicationAccountSettingsView(mixins.AdminMixin,
                                     ApplicationAccountBaseView, generic.UpdateView):
    """
    Application settins for client account
    """
    success_url = reverse_lazy('investment:applicationaccount_list')
    template_name = 'common/form.html'
    cancel_url = success_url
    success_message = 'Configurações salvas com sucesso!'
    title = 'Configuração de conta de cliente'
    application_form = ApplicationFormType.ACCOUNT_SETTINGS

    def get_object(self, queryset=None):
        # The pk passed to the view belongs to applicationaccount object,
        # used only to load correct application model class.
        # This return the correct objet according to the accont settings model
        # define in the application model class.
        return self.application.settings


class ApplicationDepositBaseView(ApplicationAccountBaseView, generic.CreateView):
    """
    Base view for deposit
    """

    # pylint: disable=no-member
    success_url = reverse_lazy('investment:applicationaccount_list')
    cancel_url = success_url
    template_name = 'investment/operation_form.html'
    success_message = 'Aporte agendado com sucesso!'
    title = 'Solicitação de aporte'
    application_form = ApplicationFormType.DEPOSIT

    def get_context_data(self, **kwargs):
        """
        Company context
        """
        context = super().get_context_data(**kwargs)
        # pylint: disable=no-member
        company = Company.objects.last()
        if company:
            context['bank_info'] = company
            context['bank_info'].description = 'Conta para depósito'
        return context


class ApplicationDepositView(mixins.AdminMixin, ApplicationDepositBaseView):
    """
    View for deposit
    """


class ApplicationWithdrawBaseView(ApplicationAccountBaseView, generic.CreateView):
    """
    Base view for withdraw
    """

    # pylint: disable=no-member
    success_url = reverse_lazy('investment:applicationaccount_list')
    cancel_url = success_url
    template_name = 'investment/operation_form.html'
    success_message = 'Resgate agendado com sucesso!'
    title = 'Solicitação de resgate'
    application_form = ApplicationFormType.WITHDRAW

    def get_context_data(self, **kwargs):
        """
        Company context
        """
        context = super().get_context_data(**kwargs)
        # pylint: disable=no-member
        user = self.application_account.user
        bank_info = user.bankaccount_set.filter(main_account=True).last()
        if bank_info:
            context['bank_info'] = dict()
            context['bank_info']['name'] = user.get_full_name()
            context['bank_info']['cpf'] = user.client.cpf
            context['bank_info']['cnpj'] = user.client.cnpj
            context['bank_info']['bank'] = bank_info.bank
            context['bank_info']['bank_branch'] = bank_info.branch
            context['bank_info']['bank_account'] = bank_info.account
            context['bank_info']['description'] = 'Conta para depósito'
        return context


class ApplicationWithdrawView(mixins.AdminMixin, ApplicationWithdrawBaseView):
    """
    Base view for withdraw
    """

    # pylint: disable=no-member
    success_url = reverse_lazy('investment:applicationaccount_list')
    cancel_url = success_url
    success_message = 'Resgate agendado com sucesso!'
    title = 'Solicitação de resgate'
    application_form = ApplicationFormType.WITHDRAW


class ApplicationApprovalView(mixins.AdminMixin, ApplicationAccountBaseView, generic.UpdateView):
    """
    View for withdraw
    """

    # pylint: disable=no-member
    success_url = reverse_lazy('investment:moneytransfer_list')
    cancel_url = success_url
    template_name = 'common/form.html'
    success_message = 'Transferência avaliada com sucesso!'
    title = 'Aprovação de trasferência'
    application_form = ApplicationFormType.OPERATION_APPROVAL

    def get_application_account(self, object_pk):
        """
        Application account
        """
        # pylint: disable=no-member
        return MoneyTransfer.objects.get(pk=object_pk).application_account


class ApplicationCompletionView(mixins.AdminMixin, ApplicationAccountBaseView, generic.UpdateView):
    """
    View for withdraw
    """

    # pylint: disable=no-member
    success_url = reverse_lazy('investment:accop_schedule_list')
    cancel_url = success_url
    template_name = 'common/form.html'
    success_message = 'Operação finalizada com sucesso!'
    title = 'Conclusão de trasferência'
    application_form = ApplicationFormType.OPERATION_COMPLETION

    def get_application_account(self, object_pk):
        """
        Application account
        """
        # pylint: disable=no-member
        return MoneyTransfer.objects.get(pk=object_pk).application_account

    def get_controls(self):
        controls = super().get_controls()
        del controls[1]
        return controls


class ApplicationOperationView(ApplicationBaseView):
    """
    Settings for application created fom application model
    """

    success_url = reverse_lazy('investment:application_list')
    template_name = 'common/form.html'
    cancel_url = success_url
    success_message = 'Operação realizada com sucesso!'
    title = 'Operação financeira'
    application_form = ApplicationFormType.APPLICATION_OPERATION
    confirm_operation = 'save'

    def get_controls(self):
        controls = super().get_controls()
        # removing 'Save and continue' control
        del controls[1]
        if self.has_form:
            # Change save button text according to the application
            action_name = self.form.get_action_name(self.application)
            if action_name:
                controls[1].text = action_name
            else:
                del controls[1]
        else:
            del controls[1]
        return controls

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.has_form:
            kwargs['user'] = self.request.user
            self.title = self.form.operation_name
        return kwargs
