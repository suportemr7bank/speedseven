"""
Application models
"""

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from investment.interfaces.base import ApplicationSettingBaseModel
from investment.interfaces.validators import (
    validate_greate_than_zero, validate_null_or_greate_than_zero)
from investment.models import Application, ApplicationAccount


class ApplicationSettings(ApplicationSettingBaseModel):
    """
    Application model settings
    """

    class Meta:
        """
        Meta class
        """
        verbose_name = 'Configuração da aplicação'
        verbose_name_plural = 'Configurações das aplicações'

    application = models.OneToOneField(
        Application, verbose_name='Aplicação',
        related_name='pool_account_settings', on_delete=models.CASCADE, editable=False)

    min_initial_deposit = models.FloatField(
        verbose_name='Depósito inicial mínimo',
        help_text='Valor inicial aceito para abertura de conta',
        validators=[validate_greate_than_zero]
    )

    min_deposit = models.FloatField(
        verbose_name='Depósito mínimo',
        help_text='Valor mínimo para depósito após abertura de conta',
        validators=[validate_greate_than_zero]
    )

    deposit_term = models.IntegerField(
        verbose_name='Prazo para aporte (dias)',
        help_text='Prazo para o aporte ser compensado',
        validators=[MinValueValidator]
    )

    withdraw_account_term = models.IntegerField(
        verbose_name='Prazo para resgate da carteira (dias)',
        validators=[MinValueValidator]
    )

    withdraw_income_term = models.IntegerField(
        verbose_name='Prazo para resgate do rendimento (dias)',
        validators=[MinValueValidator]
    )

    value_threshold = models.FloatField(
        verbose_name='Valor limite',
        help_text='Contas com valor acima deste tem prazo de resgate especial',
        validators=[MinValueValidator]
    )

    withdraw_threshold_term = models.IntegerField(
        verbose_name='Prazo para resgate acima do valor limite (dias)',
        help_text='Todo resgate acima do valor limite obedecerá este prazo',
        validators=[MinValueValidator]
    )


class AccountSettings(models.Model):
    """ Application model settings"""

    class Meta:
        """
        Meta class
        """
        verbose_name = 'Configuração da conta do cliente'
        verbose_name_plural = 'Configurações das contas dos clientes'

    application_account = models.OneToOneField(
        ApplicationAccount, verbose_name='Aplicação', on_delete=models.CASCADE, editable=False)

    custom_rate = models.FloatField(
        verbose_name='Percentual especial',
        help_text='Sobrepõe o valor de aporte padrão da aplicação somente para este cliente',
        null=True, blank=True,
        validators=[validate_null_or_greate_than_zero]
    )

    min_initial_deposit = models.FloatField(
        verbose_name='Depósito mínimo inicial',
        help_text='Depósito mínimo específico para o cliente',
        null=True, blank=True,
        validators=[validate_null_or_greate_than_zero]
    )

    deposit_term = models.IntegerField(
        verbose_name='Prazo para aporte em dias',
        help_text='Prazo de compensação de aporte específico para o cliente',
        null=True, blank=True,
        validators=[MinValueValidator]
    )


class IncomeOperation(models.Model):
    """
    Register operation data
    """

    class State(models.TextChoices):
        """
        Income operation state
        """
        WATING = 'WAIT', 'Aguardando'
        FINISHED = 'FINI', 'Finalizado com sucesso'
        RUNNING = 'RUNN', 'Calculando'
        ERROR = 'ERRO', 'Finalizado com erros'

    application = models.ForeignKey(
        Application, verbose_name='Aplicação', on_delete=models.CASCADE, editable=False)

    state = models.CharField(verbose_name='Situação', max_length=4, choices=State.choices,
                             default=State.WATING)

    income_date = models.DateField(verbose_name='Mês do cálculo')

    date_created = models.DateTimeField(
        verbose_name='Data de criação', auto_now_add=True)

    date_started = models.DateTimeField(
        verbose_name='Início da operação', null=True, blank=True)

    date_finished = models.DateTimeField(
        verbose_name='Fim da operação', null=True, blank=True)

    full_rate = models.FloatField(
        verbose_name='Percentual cheio', validators=[validate_greate_than_zero])

    costs_rate = models.FloatField(verbose_name='Custos', validators=[validate_greate_than_zero])

    net_rate = models.FloatField(
        verbose_name='Percentual líquido', validators=[validate_greate_than_zero])

    paid_rate = models.FloatField(
        verbose_name='Percentual pago', validators=[validate_greate_than_zero])

    error_message = models.CharField(
        max_length=1000, null=True, blank=True, editable=False)

    operator = models.ForeignKey(settings.AUTH_USER_MODEL,
                                 verbose_name='Operador', on_delete=models.CASCADE)
