"""
Client backgroud tasks
"""

import smtplib

from allauth.account.adapter import DefaultAccountAdapter
from celery import shared_task
from celery.utils.log import get_task_logger
from django.core import mail
from django.db.models import CharField, F, Value
from django.db.models.functions import Concat
from django.utils import timezone

from clients.models import Client

logger = get_task_logger(__name__)


@shared_task
def send_anniversary_email():
    """
    Send anniversary email to active clients
    """
    today = timezone.datetime.now()
    month = today.month
    day = today.day

    # pylint: disable=no-member
    clients = Client.objects.filter(
        birth_date__month=month,
        birth_date__day=day,
        user__is_active=True
    ).annotate(
        email=F('user__email'),
        name=Concat(
            'user__first_name',
            Value(' '),
            'user__last_name',
            output_field=CharField())).values('email', 'name')

    if clients:
        template_prexix = 'clients/email/client_anniversary'
        email_list = []
        adapter = DefaultAccountAdapter()

        for client in clients:
            context = {
                'name': client['name'],
                'email': client['email']
            }
            msg = adapter.render_mail(
                template_prefix=template_prexix,
                email=client['email'],
                context=context
            )
            email_list.append(msg)

        connection = mail.get_connection()
        connection.open()
        sent_count = 0

        for message in email_list:
            try:
                sent_count += message.send()
            except smtplib.SMTPException as exc:
                logger.info('Email anniversary: error (%s)', str(exc))
            except ConnectionRefusedError as exc:
                logger.info('Email anniversary: error (%s)', str(exc))

        logger.info('Email anniversary:  (%s) emails sent', sent_count)
        connection.close()
    else:
        logger.info('Email anniversary: no clients anniversary email to send')
