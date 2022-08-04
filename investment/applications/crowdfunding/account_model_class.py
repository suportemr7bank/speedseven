"""
Application definitions
"""

from django.db.models import Sum, Count
from django.urls import reverse

from investment.interfaces.base import ApplicationModelClassBase
from investment.interfaces import enums

from common.formats import decimal_format

from . import forms, models, agreement_renderer


class Crowdfunding(ApplicationModelClassBase):
    """
    Class with application definitons
    """
    settings_related_name = 'crowdfunding_settings'
    application_settings_form = forms.ApplicationSettingsForm
    application_purchase_form = forms.ApplicationPurchaseForm
    application_operation_form = forms.OperationForm
    deposit_form = forms.DepositForm
    operation_approval_form = forms.OperationApprovalForm

    @classmethod
    def aplication_post_create(cls, application):
        super().aplication_post_create(application)
        # pylint: disable=no-member
        models.ApplicationSettings.objects.create(
            application=application,
        )

    @classmethod
    def aplication_account_post_create(cls, application_account) -> enums.PostCreateState:
        return enums.PostCreateState.CREATED

    @classmethod
    def get_form(cls, form: enums.ApplicationFormType, application_account=None):
        if form == enums.ApplicationFormType.DEPOSIT:
            deposit_state = application_account.applicationdeposit.state
            state = models.ApplicationDeposit.State
            if deposit_state in [state.REQUESTED, state.COMPLETED]:
                return None
        return super().get_form(form)

    @classmethod
    def get_widget_template(cls, application_account, theme=None):
        widget = cls.get_application_info(
            application_account.application, theme)

        application_deposit = getattr(
            application_account, 'applicationdeposit', None)

        if application_deposit:
            widget += '''
            <div class="mt-4"> Valor do seu contrato: $value</div>
            '''.replace('$value', decimal_format(application_deposit.value))

            settings = application_account.application.settings
            state = models.ApplicationSettings.State

            url = reverse('clients:deposit_create', kwargs={
                'pk': application_account.pk})
            if settings.state == state.OPEN_DEPOSIT:
                if application_deposit.state == models.ApplicationDeposit.State.WAITNG:
                    widget += '''
                    <a href="$url" class="mt-4 btn btn-success">Realize seu depósito agora</a>
                    '''.replace('$url', url)
                elif application_deposit.state == models.ApplicationDeposit.State.REQUESTED:
                    widget += '''
                    <p class="mt-4 text-success">Depósito em análise</p>
                    '''
                elif application_deposit.state == models.ApplicationDeposit.State.REFUSED:
                    error = application_account.applicationdeposit.money_transfer.error_message or "---"
                    receipt_url = application_account.applicationdeposit.money_transfer.receipt_file.url
                    widget += '''
                    <p class="mt-4">Depósito reprovado: <a href="$receipt_url" class="text-success">$err</a></p>
                    <a href="$url" class="btn btn-success mt-4">Refazer depósito</a>
                    '''.replace('$url', url).replace('$err', error).replace('$receipt_url', receipt_url)
                elif application_deposit.state == models.ApplicationDeposit.State.COMPLETED:
                    widget += '''
                    <div class="mt-4 text-success">Depósito realizado</div>
                    '''
            else:
                widget += '''
                <div class="mt-4 text-success">Quando a meta for atingida seu depósito será liberado</div>
                '''

        return widget

    @classmethod
    def get_application_info(cls, application, theme=None):
        amount_str = application.crowdfunding_settings.fund_amount_str
        #pylint: disable=no-member
        query = models.ApplicationDeposit.objects.filter(
            application_account__application=application,
        ).aggregate(deposit=Sum('value'), count=Count('pk'))

        deposit = query['deposit'] or 0
        invs = query['count'] or 0

        amount = application.crowdfunding_settings.fund_amount
        percent = deposit / amount * 100

        equity = application.settings.equity_interest_str

        info = (
            '''
            <div class="pb-2"> Participação societária:</div>
            <div class="pb-2"> $amount por $equity%</div>
            <div class="progress">
                <div class="progress-bar bg-success text-dark text-center"
                     role="progressbar"
                     style="width: $percent%;"
                     aria-valuenow="$percent"
                     aria-valuemin="0"
                     aria-valuemax="100">
                </div>
            </div>
            <div class="row m-0 p-0 mt-2">
                <div class="col-6 mx-0 px-0 text-center border-end"> Captado $deposit </div>
                <div class="col-6 mx-0 px-0 text-center"> Investidores $invs </div>
            </div>
            '''.replace(
                '$percent', str(percent)
            ).replace(
                '$equity', str(equity)
            ).replace(
                '$amount', amount_str
            ).replace(
                '$deposit', decimal_format(deposit)
            ).replace(
                '$invs', str(invs)
            )
        )
        return info

    @classmethod
    def get_agreement_class(cls):
        """
        Class to render products product agreement
        """
        return agreement_renderer.ClientAgreementRenderer
