"""
Investiment forms
"""
from constance import config
from crispy_forms.helper import FormHelper, Layout
from crispy_forms.layout import HTML, Row, Column
from django import forms
from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model

from accounts import roles
from core import workflow
from common import formats
from common.forms.fields import DatePickerInput, Select2Widget, UserWidget
from common.forms.mixins import UserNameEmailFilterMixin

from . import models
from .operations.operations import ApplicationAccountOperation


class DirectOpFormBase(formats.DecimalFieldFormMixin, forms.ModelForm):
    """
    Base form for direct operations
    """

    decimal_fields = {
        'value': 2
    }

    class Meta:
        """
        Meta class
        """
        model = models.ApplicationOp
        fields = ['operation_type', 'value', 'operation_date', 'description']

        widgets = {
            'operation_date': DatePickerInput(options={'dateFormat': 'd/m/Y'})
        }

    def __init__(self, *args, **kwargs):
        self.application_account = kwargs.pop('application_account')
        self.operator = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['operation_date'].required = False
        self.app_op = ApplicationAccountOperation()

        last_op = self.application_account.applicationop_set.last()
        if last_op:
            balance = last_op.balance
            operation_date = timezone.localtime(
                last_op.operation_date).strftime('%d/%m/%Y %H:%M:%S')
        else:
            balance = 0
            operation_date = '-----'

        self.set_layout(balance, operation_date)

    def set_layout(self, balance, operation_date):
        """ Set layout """
        self.helper = FormHelper()
        fields = [
            HTML(f'<p>{self.application_account.user.get_full_name()}</p>'),
            HTML(f'<p> Última operação: {operation_date} </p>'),
            HTML(
                f'<p class="pb-4"> <strong>Saldo da aplicação:</strong> R${formats.decimal_format(balance)}</p>'),
        ]
        fields = fields + [key for key, value in self.fields.items()]
        self.helper.layout = Layout(*fields)

    def _get_operation_date(self, cleaned_data):
        operation_date = cleaned_data.get('operation_date')
        if not operation_date:
            operation_date = timezone.localtime(timezone.now())
        return operation_date

    def save(self, commit=False):
        operation_date = self._get_operation_date(self.cleaned_data)

        # pylint: disable=assignment-from-none
        obj = self.make_operation(operation_date)
        return obj

    # pylint: disable=unused-argument
    def make_operation(self, operation_date):
        """
        Make application operation
        """
        return None


class DepositiForm(DirectOpFormBase):
    """
    Deposit form
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['operation_type'].choices = models.ApplicationOp.OperationType.deposit_choices

    def clean(self):
        cleaned_data = super().clean()
        opeartion_date = self._get_operation_date(cleaned_data)
        self.app_op.validate_deposit(
            application_account=self.application_account,
            value=self.cleaned_data['value'], operation_date=opeartion_date)
        return cleaned_data

    def make_operation(self, operation_date):
        return self.app_op.make_deposit(
            operator=self.operator,
            application_account=self.application_account,
            value=self.cleaned_data['value'],
            description=self.cleaned_data['description'],
            operation_date=operation_date)


class WithdrawForm(DirectOpFormBase):
    """
    Withdraw form
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['operation_type'].choices = models.ApplicationOp.OperationType.withdraw_choices

    def clean(self):
        cleaned_data = super().clean()
        opeartion_date = self._get_operation_date(cleaned_data)
        self.app_op.validate_withdraw(
            application_account=self.application_account,
            value=self.cleaned_data['value'],
            operation_type=self.cleaned_data['operation_type'],
            operation_date=opeartion_date
        )
        return cleaned_data

    def make_operation(self, operation_date):
        operation_type = self.cleaned_data['operation_type']
        return self.app_op.make_withdraw(
            operator=self.operator,
            application_account=self.application_account,
            value=self.cleaned_data['value'],
            operation_type=operation_type,
            description=self.cleaned_data['description'],
            operation_date=operation_date)


class CloseApplicationForm(DirectOpFormBase):
    """
    Close application form
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('value')

    def make_operation(self, operation_date):
        return self.app_op.close_application(
            operator=self.operator,
            application_account=self.application_account,
            description=self.cleaned_data['description'],
            operation_date=operation_date
        )

    def set_layout(self, balance, operation_date):
        """ Set layout """
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML(
                '<div class="alert-warning p-2">'
                '   <p class="m-1 p-0"> Atenção!!! Esta operação não pode ser desfeita</p>'
                '   <p class="m-1 p-0">O saldo em conta será zerado e a aplicação desativada</p>'
                '</div>'
            ),
            HTML(
                f'<p class="pt-4">{self.application_account.user.get_full_name()}</p>'),
            HTML(f'<p> Última operação: {operation_date} </p>'),
            HTML(
                f'<p class="pb-4"> <strong>Saldo da aplicação:</strong> R${balance}</p>'),
            'operation_date',
            'description'
        )


class ApplicationAccountForm(forms.ModelForm):
    """
    Base form for operations
    """

    class Meta:
        """
        Meta class
        """
        model = models.ApplicationAccount
        fields = ['user', 'application']

    def __init__(self, *args, **kwargs):
        self.operator = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        user_model = get_user_model()
        self.fields['user'] = forms.ModelChoiceField(
                user_model.objects.filter(userrole__role=roles.Roles.CLIENT),
                widget=UserWidget(), label='Cliente', required=False)
        self.fields['user'].required=True

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.operator = self.operator
        if commit:
            with transaction.atomic():
                created = self.instance.pk is not None
                obj.save()
                if not created:
                    obj.post_create()
        return obj


class ApplicationForm(forms.ModelForm):
    """
    Base form for operations
    """

    class Meta:
        """
        Meta class
        """
        model = models.Application
        exclude = ['is_active']

    def __init__(self, *args, **kwargs):
        self.operator = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['application_model'].disabled = True

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.operator = self.operator
        if commit:
            with transaction.atomic():
                created = self.instance.pk is not None
                obj.save()
                if not created:
                    app_class = obj.application_class
                    app_class.aplication_post_create(obj)
                    obj.date_activated = timezone.localtime(timezone.now())
                obj.save()
        return obj


class ApplicationModelForm(forms.ModelForm):
    """
    Base form for operations
    """

    class Meta:
        """
        Meta class
        """
        model = models.ApplicationModel
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        self.operator = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['app_model_class'].disabled = True

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.operator = self.operator
        if commit:
            obj.save()
        return obj


class BankWidget(Select2Widget):
    """
    Widget for django_select2
    """
    search_fields = [
        "name__icontains",
        "code__icontains",
    ]


class BankAccountForm(workflow.ApprovalWorkflowFormMixin, forms.ModelForm):
    """
    Create a user bank account and insert logged user
    """

    class Meta:
        """
        Meta class
        """
        model = models.BankAccount
        fields = '__all__'
        widgets = {'bank': BankWidget}

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        self.operator = kwargs.pop('operator')
        super().__init__(*args, **kwargs)
        self.fields['bank'].required = True
        self.fields['bank_branch_number'].required = True
        self.fields['account_number'].required = True
        self.helper = FormHelper()
        self._set_layout()

        if self.operator.is_superuser:
            # User is selected in form
            user_model = get_user_model()
            self.fields['user'] = forms.ModelChoiceField(
                user_model.objects.filter(userrole__role=roles.Roles.CLIENT),
                widget=UserWidget(), required=False)
            self.fields['user'].required=True
            if self.instance.pk:
                self.fields['user'].disabled = True
        else:
            # User is the logged user (self.user)
            self.fields.pop('user')
            if not self.instance.pk:
                if self.user.bankaccount_set.count() == 0:
                    self.initial['main_account'] = True
                    self.fields['main_account'].disabled = True
            else:
                if self.user.bankaccount_set.count() >= 1 and self.instance.main_account:
                    self.fields['main_account'].disabled = True

    def _set_layout(self):
        """
        Set layout
        """
        self.helper.layout = Layout(self.workflow_layout,
                                    Row(Column('user'), Column(
                                        HTML('')), Column(HTML(''))),
                                    Row(Column('bank'), Column(
                                        HTML('')), Column(HTML(''))),
                                    Row(Column('bank_branch_number'), Column(
                                        'bank_branch_digit'), Column(HTML(''))),
                                    Row(Column('account_number'), Column(
                                        'account_digit'), Column(HTML(''))),
                                    Row(Column('main_account'), Column(
                                        HTML('')), Column(HTML(''))),
                                    )

    def _get_user(self):
        # Use only after clean method
        if self.operator.is_superuser:
            user = self.cleaned_data.get('user')
        else:
            user = self.user
        return user

    def clean(self):
        # count() reffers to registered accounts.
        # The current account saved is not registered yet
        cleaned_data = super().clean()

        user = self._get_user()
        if user and not self.instance.pk:
            max_acc = config.MAX_BANK_ACCOUNT_NUMBER
            if user.bankaccount_set.count() >= max_acc:
                self.add_error(
                    '',
                    f"Cada cliente pode ter no máximo {max_acc} contas cadastradas."
                )
        return cleaned_data

    def save(self, commit=True):
        """
        Insert logged user to bank account
        """
        bankaccount = super().save(commit=False)
        if commit:
            if not getattr(bankaccount, 'user', None):
                bankaccount.user = self.user

            bankaccount.operator = self.operator
            bankaccount.save()
            if bankaccount.main_account:
                user = self._get_user()
                user.bankaccount_set.exclude(pk=bankaccount.pk).filter(
                    main_account=True).update(main_account=False)
        return bankaccount


class BankFilterForm(UserNameEmailFilterMixin):
    """
    Used to show a filter in the bank list view
    """
    model_user_field = 'user'