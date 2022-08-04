"""
Application forms
"""

import calendar

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Layout, Row, HTML
from django import forms
from django.conf import settings
from django.utils import timezone
from django.db import transaction

from common import formats
from common.forms.fields import DatePickerInput

from investment.interfaces.forms import (ApplicationOperationFormBase, MoneyTransfer, MoneyTransferFormBase,
                                         ApplicationSettingsFormMixin, OperationApprovalFormMixin)
from investment.operations.operations import ApplicationAccountOperation

from .models import AccountSettings, ApplicationSettings, IncomeOperation

from . import tasks


class ApplicationSettingsForm(formats.DecimalFieldFormMixin, ApplicationSettingsFormMixin, forms.ModelForm):
    """ Application settings"""

    decimal_fields = {
        'min_initial_deposit': 2,
        'min_deposit': 2,
        'value_threshold': 2
    }

    class Meta:
        """
        Meta class
        """
        model = ApplicationSettings
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._set_laytout()

    def _set_laytout(self):
        self.helper.layout.extend([
            Row(
                Column('min_initial_deposit'),
                Column('min_deposit'),
            ),
            Row(
                Column('deposit_term'),
                Column(HTML('')),
            ),
            Row(
                Column('withdraw_account_term'),
                Column('withdraw_income_term')
            ),
            Row(
                Column('withdraw_threshold_term'),
                Column('value_threshold'),
                css_class='pb-4'
            ), ]
        )


class AccountSettingsForm(formats.DecimalFieldFormMixin, forms.ModelForm):
    """ Application account settings"""

    decimal_fields = {
        'custom_rate': 2,
        'min_initial_deposit': 2,
    }

    class Meta:
        """
        Meta class
        """
        model = AccountSettings
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        self.application_account = kwargs.pop('application_account')
        if acc_settings := getattr(self.application_account, 'accountsettings', None):
            kwargs['instance'] = acc_settings
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.application_account = self.application_account
        if commit:
            obj.save()
        return obj


class OperationTerm:
    """
    Check operation term in application settings
    """

    @staticmethod
    def deposit_term(money_tranfer):
        """
        Deposit term in days
        """
        acc = money_tranfer.application_account
        if account_deposit_term := acc.accountsettings.deposit_term:
            term = account_deposit_term
        elif application_deposit_term := acc.application.settings.deposit_term:
            term = application_deposit_term
        else:
            term = None
        return term

    @staticmethod
    def withdraw_term(money_tranfer):
        """
        Witdraw term in days
        """
        app_settings = money_tranfer.application_account.application.settings
        if money_tranfer.value > app_settings.value_threshold:
            term = app_settings.withdraw_threshold_term
        else:
            if money_tranfer.operation == MoneyTransfer.Operation.WITHDRAW_INCOME:
                term = app_settings.withdraw_income_term
            elif money_tranfer.operation == MoneyTransfer.Operation.WITHDRAW_WALLET:
                term = app_settings.withdraw_account_term
        return term


class TransferFormBase(MoneyTransferFormBase):
    """
    Money transfer form
    """

    operation_class = ApplicationAccountOperation

    def deposit_term_days(self, money_tranfer):
        """
        Term form deposit operation
        """
        return OperationTerm.deposit_term(money_tranfer)

    def withdraw_term_days(self, money_tranfer):
        """
        Term form withdraw operation
        """
        return OperationTerm.withdraw_term(money_tranfer)


class DepositForm(TransferFormBase):
    """
    Deposit form
    """
    transfer_operation = MoneyTransfer.Operation.DEPOSIT

    def clean(self):
        cleaned_data = super().clean()
        acc = self.application_account

        approval = self.cleaned_data.get('approve', None)
        if approval == 'approved' and not cleaned_data.get('receipt_file', None):
            self.add_error('receipt_file', 'Aprovação requer comprovante')

        # First deposit rule
        if value := cleaned_data.get('value', None):
            if not acc.applicationop_set.exists():
                if acc_min := acc.accountsettings.min_initial_deposit:
                    if value < acc_min:
                        self.add_error(
                            'value', f'O depósito inicial deve ser maior ou igual a {acc_min}')
                elif app_min := acc.application.settings.min_initial_deposit:
                    if value < app_min:
                        self.add_error(
                            'value', f'O depósito inicial deve ser maior ou igual a {app_min}')
            else:
                app_min = acc.application.settings.min_deposit
                if value < app_min:
                    self.add_error(
                        'value', f'Depósito mínimo permitido maior ou igual a {app_min}')

        return cleaned_data


class WithdrawForm(TransferFormBase):
    """
    Withdraw form
    """
    transfer_operation = MoneyTransfer.Operation.WITHDRAW_WALLET

    class Meta(TransferFormBase.Meta):
        """
        Meta class
        """
        model = MoneyTransfer
        fields = ['operation', 'value', 'receipt_file', 'display_message']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['operation'].choices = MoneyTransfer.Operation.withdraw_choices()
        self.fields['receipt_file'].required = False
        if not self.user.is_superuser:
            self.fields['receipt_file'].disabled = True
            self.fields['receipt_file'].widget = forms.HiddenInput()

        income_balance = self.application_account.income_balance
        balance = self.application_account.balance
        blocked_balance = balance - income_balance

        fields = [
            HTML('<p class="h4 text-success"> <strong> Saldos disponívies</strong></p>'),
            HTML(
                f'<p class="p-0 mb-2"> - Resgate do rendimento: R${formats.decimal_format(income_balance)}</p>'),
            HTML(
                f'<p class="pt-0 pb-4"> - Resgate da carteira: R${formats.decimal_format(blocked_balance)}</p>'),
        ]

        if self.user.is_superuser:
            fields.insert(
                0, HTML(f'<p class="pb-3">{self.application_account.user.get_full_name()}</p>'))

        fields = fields + [key for key, value in self.fields.items()]
        self.helper.layout = Layout(*fields)

    def save(self, commit=True):
        obj = super().save(commit=False)
        if commit:
            obj.operation = self.cleaned_data['operation']
            obj.save()
        return obj


class OperationApprovalForm(OperationApprovalFormMixin, TransferFormBase):
    """
    Manual operation approval (deposit/withdraw) form
    """


class OperationCompletionForm(forms.ModelForm):
    """
    Manual operation approval (deposit/withdraw) form
    """

    app_account = forms.CharField(max_length=512, label="")

    class Meta:
        """
        Meta class
        """
        model = MoneyTransfer
        fields = ['operation', 'value', 'receipt_file', 'display_message']

    field_order = ['app_account', 'operation',
                   'value', 'display_message ', 'receipt_file']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        self.app_account = kwargs.pop('application_account')
        super().__init__(*args, **kwargs)

        self.fields['app_account'].disabled = True
        self.initial['app_account'] = self.app_account.__str__()
        self.fields['operation'].disabled = True
        self.fields['value'].disabled = True
        self.fields['display_message'].disabled = True
        self.fields['receipt_file'].disabled = True

        if self.instance.state == MoneyTransfer.State.WAITING_RECEIPT:
            self.fields['receipt_file'].disabled = False
            self.fields['receipt_file'].required = True
        elif self.instance.state == MoneyTransfer.State.WAITING_OP:
            today = timezone.localtime(timezone.now()).date()
            date = self.instance.accountopschedule.operation_date.date()
            date_str = date.strftime('%d/%m/%Y')
            if date > today:
                self.fields['do_deposit'] = forms.BooleanField(
                    label=f'Adiantar aporte de {date_str} para hoje',
                    required=True)
            elif date <= today:
                self.fields['do_deposit'] = forms.BooleanField(
                    label="Realizar aporte", required=False)

    def save(self, commit=True):
        obj = super().save(commit=False)
        if commit:
            with transaction.atomic():
                if self.cleaned_data.get('do_deposit'):
                    acc_op = ApplicationAccountOperation()
                    acc_op.make_deposit(
                        operator=self.user,
                        application_account=self.instance.application_account,
                        value=self.instance.value
                    )
                date_finished = timezone.localtime(timezone.now())
                obj.date_finished = date_finished
                obj.state = MoneyTransfer.State.FINISHED
                obj.save()
                # Terminating schedule
                schedule = obj.accountopschedule
                schedule.trial = 1
                schedule.processor = self.user
                # pylint: disable=no-member
                schedule.state = schedule._meta.model.State.FINISHED
                schedule.last_trial_date = date_finished
                schedule.save()
        return obj


class AccountIncomeForm(formats.DecimalFieldFormMixin,
                        ApplicationOperationFormBase,
                        forms.ModelForm):
    """ Application account income"""

    operation_name = 'Cálculo de rendimento'
    action_name = 'Calcular rendimento'

    decimal_fields = {
        'full_rate': 2,
        'costs_rate': 2,
        'net_rate': 2,
        'paid_rate': 2
    }

    class Meta:
        """
        Meta class
        """
        model = IncomeOperation
        fields = ['income_date', 'full_rate',
                  'costs_rate', 'net_rate', 'paid_rate']
        widgets = {
            'income_date': DatePickerInput(options={'dateFormat': 'm/Y'})
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        self.application = kwargs.pop('application')
        super().__init__(*args, **kwargs)
        #pylint: disable=no-member
        self.last_income = IncomeOperation.objects.filter(
            application=self.application).last()
        self._set_layout()

    def _set_layout(self):
        # pylint: disable=no-member
        if self.last_income:
            date = self.last_income.income_date.strftime('%d/%m/%Y')
        else:
            date = '-----'

        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML(f'<p class="mb-4">Último rendimento calculado: {date}'),
            'income_date',
            'full_rate',
            'costs_rate',
            'net_rate',
            'paid_rate'
        )

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('income_date', None):
            cleaned_data['income_date'] = cleaned_data['income_date'].replace(
                day=1)
            if self.last_income:
                month = self.last_income.income_date.month
                year = self.last_income.income_date.year
                income_date = cleaned_data['income_date']
                if income_date.month == month and income_date.year == year:
                    self.add_error(
                        'income_date', 'Já existe um rendimento nesta data')

                month_days = calendar.monthrange(year, month)[1]
                next_income = self.last_income.income_date.replace(
                    day=month_days) + timezone.timedelta(days=1)
                if income_date > next_income:
                    self.add_error(
                        'income_date', 'Não é possível pular um mês de rendimento')
                elif income_date < next_income:
                    self.add_error(
                        'income_date', 'Não é possível cálculo retroativo')

        return cleaned_data

    def save(self, commit=True):
        obj = super().save(commit=False)
        if commit:
            obj.operator = self.user
            obj.application = self.application
            obj.save()
            if settings.INCOME_OPERATION_RUN_IN_BACKGROUND:
                tasks.run_income_operation.delay(income_operation_pk=obj.pk)
            else:
                tasks.run_income_operation(income_operation_pk=obj.pk)
        return obj
