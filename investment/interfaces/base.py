"""
Application model interfaces

"""


from django.db import models

from products.agreement_render import DefaultAgreementRender


from . import enums, forms


class ApplicationSettingBaseModel(models.Model):
    """
    Base model for application settings
    """

    class Meta:
        """
        Meta class
        """
        abstract = True

    def get_state(self):
        """
        State for settings, when necessary
        """
        return "-----"

class ApplicationModelClassBase:
    """
    Base class to create application models
    """
    settings_related_name = None
    application_settings_form = forms.ApplicationSettingsDefaultForm
    application_operation_form = None
    application_purchase_form = None
    account_settings_form = None
    deposit_form = None
    withdraw_form = None
    operation_approval_form = None
    operation_completion_form = None

    @classmethod
    def get_form(cls, form: enums.ApplicationFormType, application_account=None):
        """
        Application specific forms
        """
        if form == enums.ApplicationFormType.APPLICATION_SETTINGS:
            return cls.application_settings_form
        elif form == enums.ApplicationFormType.ACCOUNT_SETTINGS:
            return cls.account_settings_form
        elif form == enums.ApplicationFormType.APPLICATION_OPERATION:
            return cls.application_operation_form
        elif form == enums.ApplicationFormType.APPLICATION_PURCHASE:
            return cls.application_purchase_form
        elif form == enums.ApplicationFormType.DEPOSIT:
            return cls.deposit_form
        elif form == enums.ApplicationFormType.WITHDRAW:
            return cls.withdraw_form
        elif form == enums.ApplicationFormType.OPERATION_APPROVAL:
            return cls.operation_approval_form
        elif form == enums.ApplicationFormType.OPERATION_COMPLETION:
            return cls.operation_completion_form

        return None

    @classmethod
    def aplication_post_create(cls, application):
        """
        Method called after application was created
        This method is called inside a transaction and should not hang
        """
        application.settings_related_name = cls.settings_related_name
        application.save()

    @classmethod
    def aplication_account_post_create(cls, application_account) -> enums.PostCreateState:
        """
        Method called after application account was created
        This method is called inside a transaction and should not hang
        """

    @classmethod
    def get_widget_template(cls, application_account, theme=None):
        """
        widget html in django template format
        """
        return None

    @classmethod
    def get_application_info(cls, application, theme=None):
        """
        html in django template format presented in product / poduct puchase page
        """
        return None

    @classmethod
    def get_agreement_class(cls):
        """
        Class to render products product agreement
        """
        return DefaultAgreementRender
