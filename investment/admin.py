"""
Admin models
"""

from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import Application, ApplicationAccount, ApplicationOp, MoneyTransfer, Bank, BankAccount, AccountOpSchedule


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    """
    Application model admin
    """


@admin.register(ApplicationAccount)
class ApplicationAccountAdmin(admin.ModelAdmin):
    """
    Application account model admin
    """


@admin.register(ApplicationOp)
class ApplicationOpAdmin(admin.ModelAdmin):
    """
    Application account operation model admin
    """


@admin.register(MoneyTransfer)
class MoneyTransferAdmin(admin.ModelAdmin):
    """
    Money transfer model admin
    """


@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    """
    Bank model admin
    """


@admin.register(BankAccount)
class BankAccountAdmin(SimpleHistoryAdmin):
    """
    Bank account model admin
    """
    readonly_fields = ['operator']


@admin.register(AccountOpSchedule)
class AccountOpScheduleAdmin(admin.ModelAdmin):
    """
    AccountOpSchedule model admin
    """
