"""
Core admin models
"""

from django.contrib import admin

from .models import (AcceptanceTerm, EmailBatchMessage, EmailBatchRecipient,
                     EmailSendFailed, User, UserAcceptanceTerm, Company, WorkflowTask)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """
    Core user model
    """


@admin.register(UserAcceptanceTerm)
class UserAcceptanceAdmin(admin.ModelAdmin):
    """
    User acecptance terms model
    """


@admin.register(AcceptanceTerm)
class AcceptanceTermAdmin(admin.ModelAdmin):
    """
    Acecptance term model
    """


@admin.register(EmailSendFailed)
class EmailSendFailedAdmin(admin.ModelAdmin):
    """
    Email send failed model
    """
    list_display = ['id', 'batch_id',
                    'batch_subject', 'batch_date', 'date_created']

    #pylint: disable=missing-function-docstring

    @admin.display(description='Batch date')
    def batch_date(self, obj):
        return obj.email_batch.date_created.strftime('%d/%m/%Y %H:%M:%S')

    @admin.display(description='Batch id')
    def batch_id(self, obj):
        return obj.email_batch.id

    @admin.display(description='Subject')
    def batch_subject(self, obj):
        return obj.email_batch.subject


@admin.register(EmailBatchRecipient)
class EmailBatchRecipienAdmin(admin.ModelAdmin):
    """
    Email batch recipien
    """
    list_display = ['batch_date', 'batch',
                    'batch_subject', 'batch_failed', 'address', 'error_message']

    search_fields = ['email_batch__pk', 'address']

    readonly_fields = ['sent']

    #pylint: disable=missing-function-docstring

    @admin.display(description='Date created')
    def batch_date(self, obj):
        return obj.email_batch.date_created.strftime('%d/%m/%Y %H:%M:%S')

    @admin.display(description='Batch')
    def batch(self, obj):
        return obj.email_batch.pk

    @admin.display(description='Subject')
    def batch_subject(self, obj):
        return obj.email_batch.subject

    def batch_failed(self, obj):
        return obj.email_batch.pk

    @admin.display(description='Email')
    def address(self, obj):
        return obj.user.email


@admin.register(EmailBatchMessage)
class EmailBatchMessageAdmin(admin.ModelAdmin):
    """
    Email batch recipien
    """
    list_display = ['id', 'subject', 'status', 'total', 'sent', 'date_created',
                    'date_finished', 'sender']


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    """
    Company user model
    """


@admin.register(WorkflowTask)
class WorkflowTaskAdmin(admin.ModelAdmin):
    """
    WorkflowTask model
    """

    list_display = ['name', 'operator', 'evaluator', 'register_id',
                    'date_created', 'date_verified']

    readonly_fields = ['evaluator']
