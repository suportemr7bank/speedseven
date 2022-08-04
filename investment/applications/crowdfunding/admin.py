"""
Admin models
"""

from django.contrib import admin
from .models import ApplicationSettings, ApplicationDeposit


@admin.register(ApplicationSettings)
class ApplicationSettingsAdmin(admin.ModelAdmin):
    """
    ApplicationSettings model admin
    """

    list_display = ['name', 'cnpj', 'state']

@admin.register(ApplicationDeposit)
class ApplicationDepositAdmin(admin.ModelAdmin):
    """
    ApplicationDeposit model admin
    """
