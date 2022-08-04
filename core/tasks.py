"""
Core backgroud tasks
"""


import channels.layers

from asgiref.sync import async_to_sync
from django.contrib.auth import get_user_model
from celery import shared_task
from celery.utils.log import get_task_logger

from core.models import EmailBatchMessage
from accounts import roles

from . import email


logger = get_task_logger(__name__)


channel_layer = channels.layers.get_channel_layer()

def _notify_channel(email_batch):
    batch_id = email_batch.id
    date = email_batch.date_finished
    data = {
        'sent': {
            'id': f'id_{batch_id}_sent',
            'value': email_batch.sent
        },
        'status': {
            'id': f'id_{batch_id}_status',
            'value': email_batch.status,
            'text': email_batch.get_status_display(),
        },
        'date_finished': {
            'id': f'id_{batch_id}_date_finished',
            'value': date.strftime('%d/%m/%Y %H:%M:%S') if date else None
        },
    }
    message = {
        'type': 'send_batch_email',
        'data': data
    }
    async_to_sync(channel_layer.group_send)('batch_email', message)


@shared_task
def send_email(email_batch_message_pk):
    """
    Sent batch email in background
    """

    batch_mail = email.BatchEmail(
        email_batch_message_pk=email_batch_message_pk,
        notify_callback=_notify_channel)

    batch_mail.send()


@shared_task
def send_client_email(subject:str, message: str, sender_user_pk, users_pk):
    """
    Schedule mail to be sent
    """

    if users_pk:

        user_model = get_user_model()

        #pylint: disable=no-member
        email_batch = EmailBatchMessage.objects.create(
            subject=subject,
            message=message,
            sender=user_model.objects.get(pk=sender_user_pk),
            role=roles.Roles.CLIENT
        )

        batch_mail = email.BatchEmail(
            email_batch_message_pk=email_batch.pk,
            users_pk=users_pk,
            notify_callback=_notify_channel)

        batch_mail.send()
