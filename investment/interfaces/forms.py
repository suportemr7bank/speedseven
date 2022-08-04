"""
Application forms interfaces

"""

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column
from django import forms
from django.db import transaction
from django.utils import timezone

from common import formats
from products.forms.products import PurchaseForm

from ..models import BankAccount, MoneyTransfer


class ApplicationSettingsFormMixin:
    """ Application settings mixin"""

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        self.application = kwargs.pop('application')
        if app_settings := self.application.settings:
            kwargs['instance'] = app_settings

        super().__init__(*args, **kwargs)
        self.fields['is_active'] = forms.BooleanField(
            label='Ativa', required=False)
        if self.application:
            self.initial['is_active'] = self.application.is_active

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(Column('is_active'))
        )

    def clean(self):
        """
        Verify settings_related_name to access related model ApplicationSettings
        from application implementation.
        """
        cleaned_data = super().clean()
        if not self.application.settings_related_name:
            self.add_error(
                '', 'Aplicação não consegue acessar configurações do modelo relacionado')
        return cleaned_data

    def save(self, commit=True):
        """
        Save application
        """
        obj = super().save(commit=False)
        obj.application = self.application
        if commit:
            self.application.is_active = self.cleaned_data['is_active']
            self.application.save()
            obj.save()
        return obj


class OperationFormBase(formats.DecimalFieldFormMixin, forms.ModelForm):
    """
    Base form for money transfer operations
    Ex: deposit, withdraw, deposit/withdraw approval, etc
    """

    decimal_fields = {
        'value': 2
    }

    class Meta:
        """
        Meta class
        """
        model = MoneyTransfer
        fields = ['value', 'receipt_file', 'display_message']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.application_account = kwargs.pop('application_account')
        super().__init__(*args, **kwargs)
        self.set_layout()

    def set_layout(self):
        """
        Set the form fields layout
        """
        # helper used by child class
        self.helper = FormHelper()

    def save(self, commit=True):
        """
        Save transfer request
        """

        obj = super().save(commit=False)

        is_automatic = False
        if account := BankAccount.get_main_account(self.application_account.user):
            is_automatic = account.automatic_transfer_available

        obj.application_account = self.application_account
        obj.is_automatic = is_automatic
        if not getattr(obj, 'operator', None):
            obj.operator = self.user
        if commit:
            obj.save()
        return obj


class OperationMixin:
    """
    Operation mixin
    """

    operation_class = None

    def exec_operation(self, money_tranfer):
        """
        Exec operation
        """
        self.operation = self.operation_class()
        if MoneyTransfer.is_deposit(money_tranfer.operation):
            self._deposit(money_tranfer)
        elif MoneyTransfer.is_withdraw(money_tranfer.operation):
            self._withdraw(money_tranfer)

    def _deposit(self, money_tranfer):
        if term := self.deposit_term_days(money_tranfer):
            self._schedule_operation(money_tranfer, term, is_automatic=True)
            money_tranfer.state = MoneyTransfer.State.WAITING_OP
        else:
            self._create_deposit_operation(money_tranfer)
            money_tranfer.state = MoneyTransfer.State.FINISHED

    def _withdraw(self, money_tranfer):
        term = self.withdraw_term_days(money_tranfer)
        self._create_witdraw_operation(money_tranfer)
        money_tranfer.state = MoneyTransfer.State.WAITING_RECEIPT
        self._schedule_operation(
            money_tranfer, term=term, is_automatic=money_tranfer.is_automatic)

    def _create_deposit_operation(self, money_transfer):
        app_op = self.operation.make_deposit(
            operator=self.user,
            application_account=self.application_account,
            value=money_transfer.value,
            description=money_transfer.display_message,
            operation_date=None,
        )
        app_op.money_transfer = money_transfer
        app_op.save()

    def _create_witdraw_operation(self, money_transfer):
        app_op = self.operation.make_withdraw(
            operator=self.user,
            application_account=self.application_account,
            value=money_transfer.value,
            operation_type=self.cleaned_data['operation'],
            description=money_transfer.display_message,
            operation_date=None,
        )
        app_op.money_transfer = money_transfer
        app_op.save()

    def _get_current_time(self):
        return timezone.localtime(timezone.now())

    def _schedule_operation(self, money_tranfer, term, is_automatic):
        operation_date = self._get_current_time() + timezone.timedelta(days=term)
        self.operation.schedule_operation(
            money_tranfer, operation_date, operator=self.user, is_automatic=is_automatic)

    def deposit_term_days(self, money_tranfer):
        """
        Term form deposit operation
        """
        return 0

    def withdraw_term_days(self, money_tranfer):
        """
        Term form withdraw operation
        """
        return 0


class MoneyTransferFormBase(OperationMixin, OperationFormBase):
    """
    Base form for money tranfer operations
    """

    transfer_operation: MoneyTransfer.Operation = None
    operation_class = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.transfer_operation is None:
            raise Exception(
                f'Transfer form unproperly configured {self.__class__}')
        self.fields['receipt_file'].required = True

        if self.user.is_superuser:
            self.fields['approve'] = forms.ChoiceField(
                label='Aprovação',
                choices=(
                    ('', '-----'),
                    ('approved', 'Marcar como aprovado ao salvar'),
                    ('delegate', 'Enviar para aprovação')
                ),
                required=True
            )

    def clean(self):
        cleaned_data = super().clean()
        value = cleaned_data.get('value')
        if value is not None:
            app_acc_op = self.operation_class()

            if MoneyTransfer.is_deposit(self.transfer_operation):
                app_acc_op.validate_deposit(
                    self.application_account, value, operation_date=None)

            elif MoneyTransfer.is_withdraw(self.transfer_operation):
                operation_type = cleaned_data.get('operation')
                app_acc_op.validate_withdraw(
                    self.application_account, value, operation_type, operation_date=None)

        return cleaned_data

    def save(self, commit=True):
        """
        Save transfer request
        """
        obj = super().save(commit=False)
        obj.operation = self.transfer_operation
        if commit:
            with transaction.atomic():
                # Just stores the request for future approval (admin)
                obj.save()
                # Admin can approve the transfer when creating it
                if self.user.is_superuser:
                    if self.cleaned_data['approve'] == 'approved':
                        self._approve(obj)
                        obj.save()
                    elif self.cleaned_data['approve'] == 'disapproved':
                        self.reprove_request(obj)
        return obj

    def _approve(self, obj):
        self.exec_operation(obj)
        obj.date_approved = obj.date_created
        obj.approver = self.user

    def reprove_request(self, obj):
        """
        To implement disapproval
        Disapproving when creating does not make sense
        """


class ApplicationPurchaseFormBase(PurchaseForm):
    """
    Purchase form base class
    Used in product purchase process when application requires some parameter passed by the user
    Not required if the application has not configuration parameter
    """


class ApplicationSettingsDefaultForm(forms.Form):
    """
    Default application settings form
    Only activate and deactivate the application
    """

    is_active = forms.BooleanField(label='Ativa', required=False)

    def __init__(self, *args, **kwargs):
        self.application = kwargs.pop('user', None)
        self.application = kwargs.pop('application', None)
        kwargs.pop('instance')
        super().__init__(*args, **kwargs)
        if self.application:
            self.initial['is_active'] = self.application.is_active
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(Column('is_active'))
        )

    def save(self, commit=True):
        """
        Save application
        """
        if commit:
            self.application.is_active = self.cleaned_data['is_active']
            self.application.save()
        return self.application


class OperationApprovalFormMixin:
    """
    Manual operation approval (deposit/withdraw) form
    """

    # Initially set to deposit but change according to MoneyTransfer object
    transfer_operation = MoneyTransfer.Operation.DEPOSIT

    class Meta:
        """
        Meta class
        """
        model = MoneyTransfer
        fields = ['operation', 'value', 'receipt_file',
                  'display_message', 'error_message']

    field_order = ['operation', 'value', 'receipt_file',
                   'display_message', 'approve', 'error_message']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['operation'].disabled = True
        self.fields['value'].disabled = True
        self.fields['display_message'].disabled = True
        self.fields['error_message'].help_text = 'Preencha somente em caso de reprovação'
        self.fields['receipt_file'].required = False
        self.fields['approve'] = forms.ChoiceField(label='Aprovação',
                                required=True,
                                choices=(
                                    ('', '-----'),
                                    ('approved', 'Aprovado'),
                                    ('disapproved', 'Reprovado'))
                                )

        state = MoneyTransfer.State

        if self.instance.pk:
            self.transfer_operation = self.instance.operation

            disable_receipt = MoneyTransfer.is_deposit(self.instance.operation)
            self.fields['receipt_file'].disabled = disable_receipt

            disable_approval = self.instance.state != state.CREATED
            self.fields['approve'].disabled = disable_approval

            if self.instance.approved:
                self.initial['approve'] = 'approved'
                self.fields['error_message'].disabled = True
            elif self.instance.state == state.ERROR:
                self.initial['approve'] = 'disapproved'
                self.fields['receipt_file'].disabled = True

    def clean(self):
        """
        Approval fields
        """
        cleaned_data = super().clean()
        if cleaned_data['approve'] == 'disapproved':
            if not self.cleaned_data['error_message']:
                self.add_error('error_message', 'Este campo é obrigatório')
        else:
            cleaned_data['error_message'] = None

        return cleaned_data

    def reprove_request(self, obj):
        """
        Reprove request
        """
        if obj.state == MoneyTransfer.State.CREATED:
            date_finished = timezone.localtime(timezone.now())
            obj.state = MoneyTransfer.State.ERROR
            obj.approver = self.user
            obj.date_finished = date_finished
            obj.save()


class ApplicationOperationFormBase:
    """
    Controls the form button text
    """

    # Shown in the form title
    operation_name = 'Operação da aplicação'
    action_name = 'Salvar'

    @classmethod
    def get_action_name(cls, application=None):
        """
        Form submit button name
        Return None to remove button
        """
        return cls.action_name
