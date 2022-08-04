"""
Application definitions
"""

from investment.interfaces.base import ApplicationModelClassBase
from investment.interfaces.enums import PostCreateState

from . import forms, models, agreement_renderer

class SimpleInterestPoolAccount(ApplicationModelClassBase):
    """
    Class with application definitons
    """
    settings_related_name = 'pool_account_settings'
    application_settings_form = forms.ApplicationSettingsForm
    account_settings_form = forms.AccountSettingsForm
    application_operation_form = forms.AccountIncomeForm
    deposit_form = forms.DepositForm
    withdraw_form = forms.WithdrawForm
    operation_approval_form = forms.OperationApprovalForm
    operation_completion_form = forms.OperationCompletionForm


    @classmethod
    def aplication_post_create(cls, application):
        super().aplication_post_create(application)
        # pylint: disable=no-member
        models.ApplicationSettings.objects.create(
            application=application,
            min_initial_deposit=10000,
            min_deposit=1000,
            deposit_term=7,
            withdraw_account_term=15,
            withdraw_income_term=10,
            value_threshold=1000000,
            withdraw_threshold_term=20
        )

    @classmethod
    def aplication_account_post_create(cls, application_account) -> PostCreateState:
        # pylint: disable=no-member
        models.AccountSettings.objects.create(
            application_account=application_account
        )
        return PostCreateState.CREATED

    @classmethod
    def get_widget_template(cls, application_account, theme=None):
        widget = '''
        <div class="tradingview-widget-container">
        <div class="tradingview-widget-container__widget"></div>
        <div class="tradingview-widget-copyright"><a href="https://br.tradingview.com/symbols/CME_MINI-NQ1!/" rel="noopener" target="_blank"><span class="blue-text">NQ1! Cotações</span></a> por TradingView</div>
        <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-mini-symbol-overview.js" async>
        {
        "symbol": "CME_MINI:NQ1!",
        "width": "100%",
        "height": "100%",
        "locale": "br",
        "dateRange": "12M",
        "colorTheme": "$theme",
        "trendLineColor": "rgba(41, 98, 255, 1)",
        "underLineColor": "rgba(41, 98, 255, 0.3)",
        "underLineBottomColor": "rgba(41, 98, 255, 0)",
        "isTransparent": true,
        "autosize": true,
        "largeChartUrl": ""
        }
        </script>
        </div>
        '''.replace('$theme', theme)
        return widget

    @classmethod
    def get_agreement_class(cls):
        return agreement_renderer.ClientAgreementRenderer
