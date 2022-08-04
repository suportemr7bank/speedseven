"""
Application forms
"""

from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Column, Layout, Row
from django import forms
from django.db.models import Count, Subquery, Sum
from django.urls import reverse
from django.utils import timezone

from common import formats
from common.forms.fields import DatePickerInput
from core import tasks
from investment.applications.crowdfunding import models
from investment.forms import BankWidget
from investment.interfaces.forms import (ApplicationOperationFormBase,
                                         ApplicationPurchaseFormBase,
                                         ApplicationSettingsFormMixin,
                                         MoneyTransfer, MoneyTransferFormBase,
                                         OperationApprovalFormMixin)

from .models import ApplicationDeposit, ApplicationSettings
from .operations import ApplicationAccountOperation


class ApplicationSettingsForm(formats.DecimalFieldFormMixin,
                              ApplicationSettingsFormMixin,
                              forms.ModelForm):
    """
    Application settings
    """

    decimal_fields = {
        'fund_amount': 2,
        'min_deposit': 2,
        'equity_interest': 2
    }

    class Meta:
        """
        Meta class
        """
        model = ApplicationSettings
        exclude = ['application', 'state', 'date_finished']

        widgets = {
            'limit_date': DatePickerInput,
            'bank': BankWidget
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._set_laytout()

    def _set_laytout(self):
        self.helper.layout.extend(
            [
                Row(
                    Column('fund_amount', 'min_deposit'),
                    Column('equity_interest', 'limit_date')
                ),
                Row(
                    Column('name', 'cnpj'),
                    Column('contact_email', 'phone'),
                    css_class='mt-4'
                ),
                Row(
                    Column('bank'),
                    Column(''),
                    css_class='mt-4'
                ),
                Row(
                    Column('bank_branch_number'),
                    Column('bank_branch_digit'),
                ),
                Row(
                    Column('account_number'),
                    Column('account_digit'),
                ),
            ]
        )


class OperationForm(ApplicationOperationFormBase,
                    forms.ModelForm):
    """
    Application settings
    """

    operation_name = 'Operação de fundo'

    selector = forms.ChoiceField(
        label='Operações do fundo', widget=forms.RadioSelect)

    class Meta:
        """
        Meta class
        """
        model = ApplicationSettings
        fields = []

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        self.application = kwargs.pop('application')
        if app_settings := self.application.settings:
            kwargs['instance'] = app_settings

        super().__init__(*args, **kwargs)

        if self.instance.state == ApplicationSettings.State.OPEN:
            self.fields['selector'].choices = (
                ('deposit', 'Liberar depósitos e comunicar clientes'),
                ('cancel', 'Cancelar fundo')
            )

        elif self.instance.state == ApplicationSettings.State.OPEN_DEPOSIT:
            self.fields['selector'].choices = (
                ('email', 'Notificar liberação de depósitos novamente'),
                ('finish', 'Finalizar depósitos e encerrar fundo'),
                ('cancel', 'Cancelar fundo')
            )
        else:
            self.fields.pop('selector', None)

        self._set_laytout()

    @classmethod
    def get_action_name(cls, application=None):
        """
        Form submit button text
        """
        state = ApplicationSettings.State
        if application.settings.state in [state.OPEN, state.OPEN_DEPOSIT]:
            return 'Executar operação'
        else:
            return None

    def _set_laytout(self):
        obj = self.instance
        date_created = obj.application.date_created.strftime(
            '%d/%m/%Y %H:%M:%S')

        #pylint: disable=no-member
        query = ApplicationDeposit.objects.filter(
            application_account__application=obj.application
        ).aggregate(contracts=Count('pk'), contracts_value=Sum('value'))

        contracts = query['contracts']
        contracts_value = query['contracts_value'] or 0

        #pylint: disable=no-member
        query = ApplicationDeposit.objects.filter(
            application_account__application=obj.application,
        ).aggregate(deposits=Count('pk'), deposits_value=Sum('value'))

        deposits = query['deposits']
        deposits_value = query['deposits_value'] or 0

        url = reverse(
            'investment:crowdfunding:application_deposit_list', kwargs={'pk': obj.pk})

        limit_date = obj.limit_date.strftime(
            "%d/%m/%Y") if obj.limit_date else '-----'

        last_deposit = timezone.localtime(obj.last_notified_deposit).strftime(
            "%d/%m/%Y %H:%M") if obj.last_notified_deposit else '-----'

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column(
                    HTML('<p class="fw-bold">Informações gerais</p>'),
                    HTML(f'<p>Meta de captação: {obj.fund_amount_str}</p>'),
                    HTML(f'<p>Data de criação: {date_created}</p>'),
                    HTML(
                        f'<p>Data limite: {limit_date}</p>'),
                    HTML(
                        f'<p>Última notificação de depósito: {last_deposit}</p>'),
                ),
                Column(
                    HTML('<p class="fw-bold">Contratos:</p>'),
                    HTML(f'<p>Realizados: {contracts}</p>'),
                    HTML(
                        f'<p>Valor: {formats.decimal_format(contracts_value)} </p>'),
                ),
                Column(
                    HTML('<p class="fw-bold">Depósitos:</p>'),
                    HTML(
                        f'<p>Realizados: {deposits} | Pendentes: {contracts - deposits}</p>'),
                    HTML(
                        f'<p>Valor depositado: {formats.decimal_format(deposits_value)}</p>'),
                    HTML(
                        f'<p><a href="{url}" class="text-success text-decoration-none fw-bold">Lista de depósitos</a></p>'),
                ),
                Row(
                    HTML('<p class="pt-4"><strong>Situação</strong>:</p>'),
                    HTML(
                        f'<p class="pb-4">{self.instance.get_state_display()}</p>')
                )
            ),
            Row('selector')
        )

    def get_current_date(self):
        """Current date"""
        return timezone.localtime(timezone.now())

    def save(self, commit=True):
        obj = super().save(commit)

        if self.cleaned_data['selector'] == 'deposit':
            obj.state = ApplicationSettings.State.OPEN_DEPOSIT
            self.send_mail(obj)

        elif self.cleaned_data['selector'] == 'email':
            self.send_mail(obj)

        elif self.cleaned_data['selector'] == 'finish':
            obj.state = ApplicationSettings.State.COMPLETED
            obj.date_finished = self.get_current_date()

        elif self.cleaned_data['selector'] == 'cancel':
            obj.state = ApplicationSettings.State.CANCELLED
            obj.date_finished = self.get_current_date()

        self.application.is_active=False

        if commit:
            obj.save()
            self.application.save()
        return obj

    def send_mail(self, obj):
        """
        Send email notifying clients to deposit the contracted value
        """
        #pylint: disable=no-member
        users = models.ApplicationDeposit.objects.filter(
            application_account__in=Subquery(
                self.application.applicationaccount_set.filter(
                    is_active=True).values('pk')
            ),
            completed=False
        ).values_list('application_account__user_id', flat=True)

        tasks.send_client_email.delay(
            subject="Solicitação de depósito",
            message=("A operação de depósito para seu investimento já está liberada."
                     " Realize o depósito para concluir seu contrato."),
            sender_user_pk=self.user.pk,
            users_pk=list(users)
        )

        obj.last_notified_deposit = self.get_current_date()


class ApplicationPurchaseForm(formats.DecimalFieldFormMixin, ApplicationPurchaseFormBase):
    """
    Create a pending peposit object after pruduct purchasing
    """

    decimal_fields = {
        'value': 2,
    }

    extra_args_fields = ['value']

    value = forms.FloatField(label="Valor do investimento")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.application = self.product.application

        amount = self.application.crowdfunding_settings.fund_amount or 0

        # pylint: disable=no-member
        query = ApplicationDeposit.objects.filter(
            application_account__application=self.application,
        ).aggregate(deposited=Sum('value'), count=Count('pk'))
        deposited = query['deposited'] or 0

        available = amount-deposited

        min_deposit = self.application.crowdfunding_settings.min_deposit or 0

        self.helper.layout = Layout(
            self.info(amount, available, min_deposit),
            'value'
        )

    def clean(self):
        cleaned_data = super().clean()
        value = cleaned_data['value']
        min_deposit = self.application.crowdfunding_settings.min_deposit
        if min_deposit:
            if value < min_deposit:
                self.add_error(
                    'value',
                    f'O valor deve ser maior ou igual a {formats.decimal_format(min_deposit)}'
                )
        else:
            if value <= 0:
                self.add_error('value', 'O valor deve ser maior do que zero')
        return cleaned_data

    def post_created(self, product_purchase):
        # pylint: disable=no-member
        ApplicationDeposit.objects.create(
            application_account=product_purchase.application_account,
            value=self.cleaned_data['value']
        )

    def info(self, amount, available, min_deposit):
        """
        Aplication info
        """
        return HTML(
            '''
            <p> Meta de arrecadação: $amount </p>
            <p> Disponível para investimento: $available </p>
            <p class="mb-4"> Valor mínimo do investimento: $min_val</p>
            '''.replace(
                '$amount', formats.decimal_format(amount)
            ).replace(
                '$available', formats.decimal_format(available)
            ).replace(
                '$min_val', formats.decimal_format(min_deposit)
            )
        )


class DepositForm(MoneyTransferFormBase):
    """
    Deposti form
    """

    transfer_operation = MoneyTransfer.Operation.DEPOSIT
    operation_class = ApplicationAccountOperation
    block_submit = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['value'].disabled = True
        self.initial['value'] = self.application_account.applicationdeposit.value_str
        self.fields.pop('display_message')


    def clean(self):
        cleaned_data = super().clean()

        application_state = self.application_account.application.settings.state

        if application_state != ApplicationSettings.State.OPEN_DEPOSIT:
            self.add_error('', 'A operação de depósito ainda não esta disponível.')

        state = self.application_account.applicationdeposit.state
        if state in [ApplicationDeposit.State.COMPLETED, ApplicationDeposit.State.REQUESTED]:
            self.add_error('value', 'Este depósito já foi solicitado')

        approval = self.cleaned_data.get('approve', None)
        if approval == 'approved' and not cleaned_data.get('receipt_file', None):
            self.add_error('receipt_file', 'Aprovação requer comprovante')

        return cleaned_data

    def save(self, commit=True):
        obj = super().save(commit)
        if self.application_account.applicationdeposit.state != ApplicationDeposit.State.COMPLETED:
            applicationdeposit = self.application_account.applicationdeposit
            if commit:
                obj.save()
                applicationdeposit.money_transfer = obj
                applicationdeposit.save()
        return obj


class OperationApprovalForm(OperationApprovalFormMixin, MoneyTransferFormBase):
    """
    Manual operation approval (deposit/withdraw) form
    """
    operation_class = ApplicationAccountOperation
