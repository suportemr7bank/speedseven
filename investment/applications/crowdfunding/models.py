"""
Application models
"""

from django.db import models

from common.formats import decimal_format
from investment.interfaces.base import ApplicationSettingBaseModel
from investment.interfaces.validators import (
    validate_null_or_greate_than_zero, validate_percentage_between_0_100)
from investment.models import (Application, ApplicationAccount, Bank,
                               MoneyTransfer)


class ApplicationSettings(ApplicationSettingBaseModel):
    """
    Application model settings
    """

    class State(models.TextChoices):
        """
        Fund state
        """
        OPEN = 'OP', 'Aberto para contratação'
        OPEN_DEPOSIT = 'OD', 'Aguardando aportes'
        COMPLETED = 'CO', 'Fundo finalizado (captação concluída)'
        CANCELLED = 'CA', 'Fundo cancelado'

    class Meta:
        """
        Meta class
        """
        verbose_name = 'Configuração da aplicação'
        verbose_name_plural = 'Configurações das aplicações'

    application = models.OneToOneField(
        Application, verbose_name='Aplicação',
        related_name='crowdfunding_settings', on_delete=models.CASCADE, editable=False)

    fund_amount = models.FloatField(
        verbose_name='Valor total do fundo',
        help_text='Valor referente à participação societária',
        validators=[validate_null_or_greate_than_zero],
        null=True, blank=True
    )

    equity_interest = models.FloatField(
        verbose_name='Participação societária (%)',
        help_text='Deve ser maior que 0 e menor que 100',
        validators=[validate_percentage_between_0_100],
        null=True, blank=True
    )

    min_deposit = models.FloatField(
        verbose_name='Depósito mínimo',
        help_text='Valor mínimo para investimento',
        validators=[validate_null_or_greate_than_zero],
        null=True, blank=True
    )

    state = models.CharField(verbose_name='Situação',
                             max_length=2, choices=State.choices, default=State.OPEN)

    limit_date = models.DateField(
        verbose_name='Data limite',
        help_text='Data limite para encerramento do fundo',
        null=True, blank=True)

    date_finished = models.DateTimeField(
        verbose_name='Data de finalização',
        help_text='Data de encerramento do fundo',
        null=True, blank=True)

    last_notified_deposit = models.DateTimeField(
        verbose_name='Última notificação de depósito',
        null=True, blank=True)

    name = models.CharField(
        max_length=256, verbose_name="Nome da empresa", null=True, blank=True)

    cnpj = models.CharField(
        max_length=20, verbose_name='CNPJ', null=True, blank=True)

    contact_email = models.EmailField(
        verbose_name="Email de contato", null=True, blank=True)

    phone = models.CharField(
        max_length=15, verbose_name='Telefone', null=True, blank=True)

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

    @property
    def fund_amount_str(self):
        """
        Fund amount string decimal formatted
        """
        return decimal_format(self.fund_amount)

    @property
    def min_deposit_str(self):
        """
        Min deposit string decimal formatted
        """
        return decimal_format(self.min_deposit)

    @property
    def equity_interest_str(self):
        """
        Equity interest string decimal formatted
        """
        return decimal_format(self.equity_interest)

    def get_state(self):
        # pylint: disable=no-member
        return self.get_state_display()


class ApplicationDeposit(models.Model):
    """
    Fund pending deposit
    """

    class State(models.TextChoices):
        """
        Deposit request state
        """
        WAITNG = 'WAI', 'Aguardando'
        REQUESTED = 'REQ', 'Solicitado'
        REFUSED = 'REF', 'Recusado'
        COMPLETED = 'COM', 'Completo'


    application_account = models.OneToOneField(
        ApplicationAccount, verbose_name='Conta do cliente', on_delete=models.CASCADE)

    date_created = models.DateTimeField(
        auto_now_add=True, verbose_name='Data de criação')

    date_completed = models.DateTimeField(
        verbose_name='Finalização do depósito', null=True, blank=True)

    value = models.FloatField(verbose_name='Valor', validators=[
                              validate_null_or_greate_than_zero], null=True, blank=True)

    # Relate account operaions to money transfer operation
    money_transfer = models.ForeignKey(
        MoneyTransfer, verbose_name='Operação de transferência',
        on_delete=models.CASCADE, null=True, blank=True)

    @property
    def value_str(self):
        """
        Decimal formatted value string
        """
        return decimal_format(self.value)

    @property
    def state(self):
        """
        Deposit was requested
        """
        state = self.State.WAITNG
        # pylint: disable=no-member
        if mon_transf := self.money_transfer:
            if mon_transf.state==MoneyTransfer.State.CREATED:
                state = self.State.REQUESTED
            elif mon_transf.state==MoneyTransfer.State.ERROR:
                state = self.State.REFUSED
            elif mon_transf.state==MoneyTransfer.State.FINISHED:
                state = self.State.COMPLETED

        return state

    @property
    def completed(self):
        """
        Check if deposit is completed (requested and approved)
        """
        return self.state == self.State.COMPLETED