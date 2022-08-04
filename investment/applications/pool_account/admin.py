from django.contrib import admin

# Register your models here.

from .models import IncomeOperation

@admin.register(IncomeOperation)
class IncomeOperationAdmin(admin.ModelAdmin):
    """
    IncomeOperation model admin
    """
