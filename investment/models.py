"""
Investment a checking accout model
"""

import pydoc

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Max, Case, Value, Count, Sum, Q
from django.utils import timezone
from django.utils.functional import classproperty
from simple_history.models import HistoricalRecords

from common import validation
from core import workflow

from .app_settings import APPLICATION_MODEL_CLASS_ROOT_PATH
from .interfaces.enums import ApplicationFormType, PostCreateState
from .operations import exceptions as op_except


def load_applitcation_model_class(class_name):
    """ Load application model class based on a root path"""
    return pydoc.locate(f'{APPLICATION_MODEL_CLASS_ROOT_PATH}.{class_name}')


class ApplicationModel(models.Model):
    """ Scritp to handle application model """

    class Meta:
        """
        Meta class
        """
        verbose_name = 'Modelo de aplicação'
        verbose_name_plural = 'Modelos de aplicação'

    name = models.CharField(max_length=128, verbose_name='Nome do modelo')

    display_text = models.CharField(
        max_length=128, verbose_name='Texto de exibição')

    app_model_class = models.CharField(
        max_length=256, verbose_name="Classe do modelo de aplicação")

    date_created = models.DateTimeField(
        verbose_name='Data de criação', auto_now_add=True, editable=False)

    is_active = models.BooleanField(verbose_name='Ativo', default=True)

    def clean(self) -> None:
        application_class = load_applitcation_model_class(self.app_model_class)
        if not application_class:
            raise ValidationError(
                {'app_model_class': 'Classe de modelo de aplicação não encontrada'})

        return super().clean()

    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name='Operador', on_delete=models.CASCADE, editable=False)

    def __str__(self) -> str:
        return f'{self.display_text}'


class Application(models.Model):
    """ Application """

    class Meta:
        """
        Meta class
        """
        verbose_name = 'Aplicação'
        verbose_name_plural = 'Aplicações'

    name = models.CharField(max_length=128, verbose_name='Nome da aplicação')

    display_text = models.CharField(
        max_length=128, verbose_name='Texto de exibição')

    application_model = models.ForeignKey(
        ApplicationModel, verbose_name='Modelo de aplicação', on_delete=models.CASCADE)

    date_created = models.DateTimeField(
        verbose_name='Data de criação', auto_now_add=True, editable=False)

    is_active = models.BooleanField(verbose_name='Ativa', default=False)

    has_application_settings = models.BooleanField(
        verbose_name='Configuração de aplicação', default=False, editable=False)

    has_account_settings = models.BooleanField(
        verbose_name='Configuração de conta', default=False, editable=False)

    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name='Operador', on_delete=models.CASCADE, editable=False)

    settings_related_name = models.CharField(
        max_length=64, editable=False, null=True, blank=True)

    @property
    def application_class(self):
        """
        Load application class defined in application model
        """
        #pylint: disable=no-member
        if getattr(self, 'application_model', None):
            return load_applitcation_model_class(self.application_model.app_model_class)
        return None

    @property
    def settings(self):
        """
        Application settings (related field in ApplicationSettings model)
        """
        related_name = self.settings_related_name
        if related_name:
            if settings_obj := getattr(self, related_name, None):
                return settings_obj
        return None

    def clean(self) -> None:
        app = self.application_class
        if app is None:
            raise ValidationError(
                {'application_model': 'Modelo de aplicação não encontrado'})
        else:
            if app.get_form(ApplicationFormType.APPLICATION_SETTINGS):
                self.has_application_settings = True

            if app.get_form(ApplicationFormType.ACCOUNT_SETTINGS):
                self.has_account_settings = True
        return super().clean()

    @property
    def state(self):
        """
        Application state from settings
        """
        if self.settings:
            return self.settings.get_state()
        return '-----'

    def __str__(self) -> str:
        return f'{self.display_text}'


class ApplicationAccount(models.Model):
    """
    User application. The income for the application is defined by the application model.
    """

    class Meta:
        """
        Meta class
        """
        verbose_name = 'Aplicação do cliente'
        verbose_name_plural = 'Aplicações dos clientes'

    class CreationStatus(models.TextChoices):
        """
        Status from application creation
        """
        CREATED = 'CRE', 'Aplicação criada'
        RUNNING = 'RUN', 'Criando aplicação'
        SCHEDULED = 'WAI', 'Agendado para criação',
        REQUESTED = 'REQ', 'Solicitado'
        ERROR = 'ERR', 'Erro'

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             verbose_name='Cliente', on_delete=models.CASCADE)

    application = models.ForeignKey(
        Application, verbose_name='Aplicação', on_delete=models.CASCADE)

    date_created = models.DateTimeField(
        verbose_name='Data de criação', auto_now_add=True, editable=False)

    date_activated = models.DateTimeField(
        verbose_name='Data de ativação', null=True, blank=True, editable=False)

    date_deactivated = models.DateTimeField(
        verbose_name='Data de desativação', null=True, blank=True, editable=False)

    is_active = models.BooleanField(verbose_name='Ativa', default=True)

    operator = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='app_acc_operator',
                                 verbose_name='Operador', on_delete=models.CASCADE, editable=False)

    creation_status = models.CharField(
        verbose_name="Situação", max_length=3,
        choices=CreationStatus.choices, default=CreationStatus.REQUESTED, editable=False)

    message = models.TextField(verbose_name='Mensagem', null=True, blank=True)

    @property
    def balance(self):
        """
        Application account object balance
        """
        # pylint: disable=no-member
        last_op = self.applicationop_set.last()
        if last_op:
            return last_op.balance
        else:
            return 0

    @property
    def income_balance(self):
        """
        Application account object income balance
        """
        # pylint: disable=no-member
        last_income_op = self.applicationop_set.filter(
            operation_type=ApplicationOp.OperationType.INCOME).last()

        value = 0
        if last_income_op:
            value = last_income_op.value

            last_income_withdraw_op = self.applicationop_set.filter(
                operation_type=ApplicationOp.OperationType.WITHDRAW_INCOME,
                pk__gt=last_income_op.pk
            ).last()

            if last_income_withdraw_op:
                value = last_income_op.value - \
                    (last_income_op.balance - last_income_withdraw_op.balance)

        return value

    def post_create(self):
        """
        Call this after creation to execute application_model post create method.
        The application model account creation can complete the process.
        Ex: creation of an external account in a broker before activate the
        user application account.
        """
        created = self.pk is not None
        if created and self.creation_status == ApplicationAccount.CreationStatus.REQUESTED:
            # pylint: disable=no-member
            app_class = self.application.application_class
            state = app_class.aplication_account_post_create(self)
            if state == PostCreateState.CREATED:
                self.creation_status = ApplicationAccount.CreationStatus.CREATED
                self.date_activated = timezone.localtime(timezone.now())
                self.message = 'Aplicação criada'
            elif state == PostCreateState.SCHEDULED:
                self.creation_status = ApplicationAccount.CreationStatus.SCHEDULED
                self.is_active = False
                self.message = 'Criação agendada'
            elif state == PostCreateState.RUNNING:
                self.creation_status = ApplicationAccount.CreationStatus.RUNNING
                self.is_active = False
                self.message = 'Executando processo de criação'
            else:
                # TODO: log error message
                self.message = ('A classe da aplicação não retornou um status'
                                ' correto (criado, agendado ou executando)')
                self.creation_status = ApplicationAccount.CreationStatus.ERROR
                self.is_active = False

            self.save()

    @staticmethod
    def total_balance(user):
        """
        User total balance in all application accounts
        """
        #pylint: disable=no-member

        op = ApplicationOp.OperationType
        query = ApplicationAccount.objects.filter(
            Q(applicationop__operation_type=op.DEPOSIT) |
            Q(applicationop__operation_type=op.OPEN) |
            Q(applicationop__operation_type=op.WITHDRAW_WALLET) |
            Q(applicationop__operation_type=op.WITHDRAW_INCOME),
            user=user,
        ).annotate(
            num_ops=Count('applicationop')
        ).annotate(
            op_type=Case(
                default=Value(op.DEPOSIT)
            )
        ).annotate(
            last_pk=Max('applicationop__pk')
        ).values(
            'last_pk', 'pk', 'op_type'
        ).values_list('last_pk', flat=True)
        value = ApplicationOp.objects.aggregate(
            total=Sum('balance', filter=Q(pk__in=list(query)))
        )
        if value['total']:
            return value['total']

        return 0

    @staticmethod
    def total_income_balance(user):
        """
        Income balance
        Total income minus income withdraw in all application accounts
        """
        #pylint: disable=no-member

        op = ApplicationOp.OperationType
        query = ApplicationAccount.objects.filter(
            Q(applicationop__operation_type=op.INCOME) |
            Q(applicationop__operation_type=op.WITHDRAW_INCOME),
            user=user,
        ).annotate(
            num_ops=Count('applicationop')
        ).annotate(
            last_pk=Max('applicationop__pk'), op=F('applicationop__operation_type')
        ).values('last_pk', 'op', 'pk')

        income_ops = list(query.filter(
            op=op.INCOME).values_list('last_pk', flat=True))
        withdraw_ops = list(query.filter(
            op=op.WITHDRAW_INCOME).values_list('last_pk', flat=True))

        value = ApplicationOp.objects.aggregate(
            income=Sum('value', filter=Q(pk__in=income_ops)),
            total_withdraw=(
                Sum('balance', filter=Q(pk__in=income_ops)) -
                Sum('balance', filter=Q(pk__in=withdraw_ops))
            )
        )

        if value['income'] and value['total_withdraw']:
            return value['income'] - value['total_withdraw']

        return 0

    def __str__(self):
        #pylint: disable=no-member
        if product := getattr(self.application, 'product'):
            return f'{self.user.get_full_name()} - {product.display_text} - ({self.pk})'
        return f'{self.user.get_full_name()} - {self.application.display_text} - ({self.pk})'


class OperationTypeStandard:
    """
    Operation standar for consystency
    models.TextChoices can't be extended
    """
    DEPOSIT = ('DEPO', 'Aporte')
    WITHDRAW_WALLET = ('WWAL', 'Restage da carteira')
    WITHDRAW_INCOME = ('WINC', 'Restage do rendimento')


def user_receipts_path(instance, filename):
    """
    media user folder
    """
    return f'private/receipts/user/{instance.application_account.user.id}/{filename}'


class MoneyTransfer(models.Model):
    """
    Money transfer table
    """

    class Meta:
        """
        Operation date
        """
        verbose_name = 'Tranferência de dinheiro'
        verbose_name_plural = 'Tranferências de dinheiro'

    class Operation(models.TextChoices):
        """
        Define operation type
        """
        DEPOSIT = OperationTypeStandard.DEPOSIT
        WITHDRAW_WALLET = OperationTypeStandard.WITHDRAW_WALLET
        WITHDRAW_INCOME = OperationTypeStandard.WITHDRAW_INCOME

        @classmethod
        def withdraw_choices(cls):
            """
            Only withdraw
            """
            wit_wal = MoneyTransfer.Operation.WITHDRAW_WALLET
            wit_inc = MoneyTransfer.Operation.WITHDRAW_INCOME
            return [(wit_inc.value, wit_inc.label), (wit_wal.value, wit_wal.label)]

    @classmethod
    def is_deposit(cls, operation):
        """
        Return true for deposit operation
        """
        return operation == cls.Operation.DEPOSIT

    @classmethod
    def is_withdraw(cls, operation):
        """
        REturn true forw withdraw operation
        """
        return operation in [cls.Operation.WITHDRAW_INCOME, cls.Operation.WITHDRAW_WALLET]

    class State(models.TextChoices):
        """
        Define processing status
        """
        CREATED = 'CREA', 'Criada'
        WAITING_OP = 'WTOP', 'Aguardando operação'
        WAITING_RECEIPT = 'WREC', 'Aguardando recibo'
        FINISHED = 'FINI', 'Finalizado'
        ERROR = 'ERRO', 'Erro'

    # To store remote generated operation id (ex: bank account deposit id)
    operation_id = models.CharField(max_length=512, null=True, blank=True)

    application_account = models.ForeignKey(
        ApplicationAccount, verbose_name='Conta', on_delete=models.CASCADE, null=True, blank=True)

    is_automatic = models.BooleanField(
        verbose_name='Transferêcia automática', default=False)

    operation = models.CharField(
        max_length=4, verbose_name='Tipo de operação', choices=Operation.choices)

    state = models.CharField(
        max_length=4, verbose_name='Situação', choices=State.choices, default=State.CREATED)

    date_created = models.DateTimeField(
        verbose_name='Criação', auto_now_add=True)

    date_approved = models.DateTimeField(
        verbose_name='Aprovado', null=True, blank=True)

    date_finished = models.DateTimeField(
        verbose_name='Finalização', null=True, blank=True)

    error_message = models.CharField(
        max_length=1024, verbose_name='Mensagem de erro', null=True, blank=True)

    display_message = models.CharField(
        max_length=1024, verbose_name='Observação', null=True, blank=True)

    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name='Operador', on_delete=models.CASCADE)

    approver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Avaliador',
        related_name='moneytrasfer_approver',
        on_delete=models.CASCADE, null=True, blank=True)

    value = models.FloatField(verbose_name='Valor da operação', validators=[
                              validation.validate_greater_than_zero])

    receipt_file = models.FileField(
        verbose_name='Comprovante',
        upload_to=user_receipts_path,
        null=True, blank=True)

    @property
    def approved(self):
        """
        Approved status
        """
        return self.state in [MoneyTransfer.State.WAITING_OP, MoneyTransfer.State.WAITING_RECEIPT, MoneyTransfer.State.FINISHED]


def get_operation_date():
    """ The current date for operations"""
    return timezone.localtime(timezone.now())


class ApplicationOp(models.Model):
    """
    Application operations
    """

    class Meta:
        """
        Operation date
        """
        verbose_name = 'Operação de aplicação'
        verbose_name_plural = 'Operações de aplicação'

        unique_together = [['application_account', 'operation_date']]

    class OperationType(models.TextChoices):
        """
        Operation definitions
        """
        OPEN = 'OPEN', 'Abertura de conta'
        DEPOSIT = OperationTypeStandard.DEPOSIT
        WITHDRAW_WALLET = OperationTypeStandard.WITHDRAW_WALLET
        WITHDRAW_INCOME = OperationTypeStandard.WITHDRAW_INCOME
        INCOME = 'INCO', 'Rendimento'
        CLOSE = 'CLOS', 'Encerramento de conta'

        @classproperty
        # pylint: disable=no-self-argument
        def withdraw_choices(cls):
            """
            Only witdraw operation choices
            """
            return [
                (cls.WITHDRAW_WALLET.value, cls.WITHDRAW_WALLET.label),
                (cls.WITHDRAW_INCOME.value, cls.WITHDRAW_INCOME.label)
            ]

        @classproperty
        # pylint: disable=no-self-argument
        def deposit_choices(cls):
            """
            Only deposit operation choices
            """
            return [
                (cls.DEPOSIT.value, cls.DEPOSIT.label),
            ]

    application_account = models.ForeignKey(
        ApplicationAccount, verbose_name='Aplicação', on_delete=models.CASCADE)

    operation_type = models.CharField(verbose_name='Tipo de operação',
                                      max_length=4, choices=OperationType.choices)

    value = models.FloatField(verbose_name='Valor')

    balance = models.FloatField(verbose_name='Saldo', validators=[
                                validation.validate_greater_than_zero])

    description = models.CharField(
        verbose_name='Descrição', max_length=128, null=True, blank=True)

    operation_date = models.DateTimeField(verbose_name='Data da operação')

    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name='Operador', on_delete=models.CASCADE, editable=False)

    # Relate account operaions to money transfer operation
    money_transfer = models.OneToOneField(
        'MoneyTransfer', verbose_name='Operação de transferência', on_delete=models.CASCADE, null=True, blank=True)

    @classmethod
    def make_deposit(cls, operator, application_account,
                     value, description=None, operation_date=None):
        """
        Make deposit
        The first deposit has OPEN operation type
        """
        if not operation_date:
            operation_date = get_operation_date()

        #pylint: disable=no-member
        last_op = application_account.applicationop_set.last()
        if last_op:
            balance = last_op.balance + value
            operation_type = ApplicationOp.OperationType.DEPOSIT
        else:
            balance = value
            operation_type = ApplicationOp.OperationType.OPEN
            application_account.date_activated = operation_date
            application_account.is_active = True
            application_account.save()

        obj = cls._create_operation(
            operator, application_account, value, description,
            operation_date, balance, operation_type)

        return obj

    @classmethod
    def validate_deposit(cls, application_account, value, operation_date=None):
        """
        Validate deposit data
        """
        if not application_account:
            raise op_except.InvalidApplicationError(
                'Aplicação inválida ou não existe')
        elif application_account and not application_account.is_active:
            raise op_except.InactiveApplicationError(
                'Esta aplicação está inativa')

        if value <= 0:
            raise op_except.DepositValueError(
                {'value': 'O valor do depósito deve ser maior que zero'})

        #pylint: disable=no-member
        last_op = application_account.applicationop_set.last()
        if last_op and operation_date:
            if operation_date == last_op.operation_date:
                raise op_except.SameOperationDateError(
                    {'operation_date': 'Já existe uma operação com esta data. Escolha uma data maior'}
                )
            elif operation_date < last_op.operation_date:
                raise op_except.ReatroactiveOperationDateError(
                    {'operation_date': 'Operação com data retroativa. Escolha uma data maior'}
                )

    @classmethod
    def make_withdraw(cls, application_account, operator,
                      value, operation_type, description=None, operation_date=None):
        """
        Make withdraw
        """

        if not operation_date:
            operation_date = get_operation_date()

        #pylint: disable=no-member
        last_op = application_account.applicationop_set.last()
        balance = last_op.balance - value

        obj = cls._create_operation(
            operator, application_account, value, description,
            operation_date, balance, operation_type)
        return obj

    @classmethod
    def validate_withdraw(cls, application_account, value, operation_type, operation_date=None):
        """
        Validate witdraw data
        """
        if not application_account:
            raise op_except.InvalidApplicationError(
                'Aplicação inválida ou não existe')
        else:
            if not application_account.applicationop_set.exists():
                raise op_except.InactiveApplicationError(
                    'Saldo inexistente. Nenhum aporte foi realizado ainda.')
            elif not application_account.is_active:
                raise op_except.InactiveApplicationError(
                    'Esta aplicação não está ativa')

        if value <= 0:
            raise op_except.WithdrawValueError(
                'O valor do depósito deve ser maior que zero')

        #pylint: disable=no-member
        last_op = application_account.applicationop_set.last()
        if operation_date:
            if operation_date == last_op.operation_date:
                raise op_except.SameOperationDateError(
                    {'operation_date': 'Já existe uma operação com esta data. Escolha uma data maior'}
                )
            elif operation_date < last_op.operation_date:
                raise op_except.ReatroactiveOperationDateError(
                    {'operation_date': 'Operação com data retroativa. Escolha uma data maior'}
                )

        if operation_type == ApplicationOp.OperationType.WITHDRAW_INCOME:
            if value > application_account.income_balance:
                raise op_except.WithdrawNotEnoughBalanceError(
                    'Saldo insuficiente para resgate do rendimento')

        elif operation_type == ApplicationOp.OperationType.WITHDRAW_WALLET:
            blocked_balance = application_account.balance - application_account.income_balance
            if value > blocked_balance:
                raise op_except.WithdrawNotEnoughBalanceError(
                    'Saldo insuficiente para resgate da carteira')

    @classmethod
    def close_application(cls, operator, application_account,
                          description=None, operation_date=None):
        """
        Make a witdraw operation to reset balance and create a close operation
        If no previous operation exists, just close the application and return None
        """
        #pylint: disable=no-member
        if application_account:
            if application_account.is_active:
                app_op = None
                last_op = application_account.applicationop_set.last()
                if last_op:
                    balance = last_op.balance

                    if balance > 0:
                        value = balance
                        cls.make_withdraw(application_account, operator,
                                          value, ApplicationOp.OperationType.WITHDRAW_WALLET,
                                          description, operation_date)

                    balance = 0
                    value = 0
                    operation_type = ApplicationOp.OperationType.CLOSE

                    if not operation_date:
                        operation_date = get_operation_date()

                    app_op = cls._create_operation(
                        operator, application_account, value, description,
                        operation_date, balance, operation_type)

                application_account.is_active = False
                application_account.date_deactivated = operation_date
                application_account.save()

                return app_op
            else:
                raise op_except.InactiveApplicationError(
                    'Esta aplicação não está ativa')
        else:
            raise op_except.InvalidApplicationError(
                'Aplicação inválida ou não existe')

    @classmethod
    def _create_operation(cls, operator, application_account, value,
                          description, operation_date, balance, operation_type):
        # pylint: disable=no-member
        obj = ApplicationOp.objects.create(
            application_account=application_account,
            operation_type=operation_type,
            value=value,
            balance=balance,
            description=description,
            operation_date=operation_date,
            operator=operator
        )
        return obj

    @classmethod
    def make_income_deposit(cls, operator_id, application_account_id,
                            value, balance, operation_date, description=None):
        """
        Make income deposit
        Qhick vertion to make deposit without any verification
        """
        # pylint: disable=no-member
        obj = ApplicationOp.objects.create(
            application_account_id=application_account_id,
            operation_type=ApplicationOp.OperationType.INCOME,
            value=value,
            balance=balance,
            description=description,
            operation_date=operation_date,
            operator_id=operator_id
        )
        return obj

    def __str__(self):
        #pylint: disable=no-member
        return f'app {self.application_account.pk} - appop {self.pk} - value: {self.balance}'


class AccountOpSchedule(models.Model):

    """
    Transferred values schedule to deposit
    """

    class Meta:
        """
        Operation date
        """
        verbose_name = 'Agendamento de operações'
        verbose_name_plural = 'Agendamentos de operaçôes'

    class State(models.TextChoices):
        """
        Define processing status
        """
        WAITING = 'WAIT', 'Aguardando'
        RUNNING = 'RUNN', 'Executanto'
        FINISHED = 'FINI', 'Finalizado'
        ERROR = 'ERRO', 'Erro'

    money_transfer = models.OneToOneField(
        MoneyTransfer, verbose_name='Transferência', on_delete=models.CASCADE)

    operation_date = models.DateTimeField(verbose_name='Data da operação')

    state = models.CharField(
        max_length=4, verbose_name='Situação', choices=State.choices, default=State.WAITING)

    max_trials = models.PositiveIntegerField(
        verbose_name='Máximo de tentativas', default=3)

    trial = models.PositiveIntegerField(
        verbose_name='Tentativas realizadas', default=0)

    date_created = models.DateTimeField(
        verbose_name='Criação', auto_now_add=True)

    last_trial_date = models.DateTimeField(
        verbose_name='Última tentativa', editable=False, null=True, blank=True)

    date_finished = models.DateTimeField(
        verbose_name='Finalização', editable=False, null=True, blank=True)

    error_message = models.CharField(
        max_length=1024, verbose_name='Mensagem de erro', null=True, blank=True)

    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name='Operador', on_delete=models.CASCADE)

    # The user which process the request (Ex: deposit approval)
    # If processing is made in background may be a user set to backgroun processing (Ex: cron_user)
    processor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Avaliador',
        related_name='accop_schedule_processor',
        on_delete=models.CASCADE, null=True, blank=True)

    is_automatic = models.BooleanField(
        verbose_name='Agendamento automático', default=False)


class Bank(models.Model):
    """
    Bank model
    """
    class Meta:
        """
        Meta class
        """
        verbose_name = 'Banco'
        ordering = ['code']

    code = models.IntegerField(verbose_name='Código', null=True, blank=True)
    name = models.CharField(verbose_name='Nome', max_length=255)
    ispb = models.IntegerField(verbose_name='ISPB', null=True, blank=True)

    def __str__(self):
        if self.code:
            return f'{self.code} - {self.name}'
        else:
            return self.name


class BankAccount(workflow.ApprovalWorkflow):
    """
    Bank account
    """

    initial_status_created = True
    task_name = 'Aprovação de conta bancária'
    form_view = 'core:bank_account_update'
    exclude_fields = ['main_account']

    class Meta:
        """
        Meta class
        """
        verbose_name = 'Conta bancária'
        verbose_name_plural = 'Contas bancárias'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bank = models.ForeignKey(Bank, verbose_name='Banco',
                             on_delete=models.CASCADE, null=True, blank=True)
    bank_branch_number = models.IntegerField(
        verbose_name='Agência', null=True, blank=True)
    bank_branch_digit = models.CharField(
        verbose_name='Dígito da agência', max_length=1, null=True, blank=True)
    account_number = models.IntegerField(
        verbose_name='Número da conta', null=True, blank=True)
    account_digit = models.IntegerField(
        verbose_name='Dígito da conta', null=True, blank=True)

    main_account = models.BooleanField(
        verbose_name="Conta principal", default=False)

    history = HistoricalRecords()

    @property
    def automatic_transfer_available(self):
        """
        Atomatic transfer between banck accounts
        """
        # TODO: implement when mr7 account is active
        return False

    @property
    def branch(self):
        """
        Bank branch
        """
        if self.bank_branch_digit:
            return f'{self.bank_branch_number}-{self.bank_branch_digit}'
        else:
            return self.bank_branch_number

    @property
    def account(self):
        """
        User bank account
        """
        if self.account_digit:
            return f'{self.account_number}-{self.account_digit}'
        else:
            return self.account_number

    @property
    def registration_completed(self):
        """
        Indicates if registration is completed
        """
        #pylint: disable=no-member
        return self.bank and self.bank_branch_number and self.account_number

    @staticmethod
    def get_main_account(user):
        """
        Return user main account if it exists
        """
        # pylint: disable=no-member
        try:
            return BankAccount.objects.get(user=user, main_account=True)
        except BankAccount.DoesNotExist:
            return None

    def __str__(self):
        #pylint: disable=no-member
        return f'{self.user.get_full_name()} - {self.bank}'
