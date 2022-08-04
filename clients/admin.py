"""
Admin models
"""

from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import Client


@admin.register(Client)
class ClientAdmin(SimpleHistoryAdmin):
    """
    Admin client model
    """
