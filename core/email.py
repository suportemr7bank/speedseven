"""
Email classes
"""
import smtplib

from celery.utils.log import get_task_logger
from django.contrib.auth import get_user_model
from django.core import mail
from django.db.models import F
from django.utils import timezone

from scheduler import lock
from core import models

logger = get_task_logger(__name__)


class BatchEmail:
    """
    Batch email class

    Email addresses from users with a role are collected in a email batch recipient
    A message list is created from recipients chunk and send
    Email batch recipients are update to indicate if sending succeded
    Failed sendings are grouped with send_failed
    Only email batch recipients which succeded are deleted

    A notify method are called, calling notify_callback with email_bach object as argument

    Warning: if chunk_size > 1 and sending fail for some message in chunk line, the sending
    will stop and remaining messages will not be sent and individual error messages will not
    be written.
    """

    def __init__(self, email_batch_message_pk, users_pk=None, notify_callback: callable = None, chunk_size=1):
        # pylint: disable=no-member
        self.email_batch = models.EmailBatchMessage.objects.get(
            pk=email_batch_message_pk)

        self.users_pk = users_pk

        self.notify_callback = notify_callback
        self.chunk_size = chunk_size

        self.subject = self.email_batch.subject
        self.message = self.email_batch.message

        # Objects with email address and sending status
        self.recipients = []

    def send(self):
        """
        Send batch or resend failed or not sent
        """
        key = f'batch_mail_{self.email_batch.pk}'
        logger.info('task key lock = %s', key)
        lock.lock_task(self._send, key=key)()

    def _send(self):

        if self.email_batch.status == models.EmailBatchMessage.Status.FINISHED:
            return
        elif self.email_batch.status == models.EmailBatchMessage.Status.WAITING:
            user_model = get_user_model()
            role = self.email_batch.role
            users_pk = self.users_pk
            if not self.users_pk:
                users_pk = list(user_model.objects.filter(
                    is_active=True, userrole__role=role).values_list('pk', flat=True))
            count = self.create_recipients(users_pk)
            self.email_batch.total = len(users_pk)
            self.email_batch.save()
        else:
            count = self.load_recipients()

        self._update_batch()
        self._notify()

        # To group failed to be sent
        send_failed = self.get_or_create_send_failed(self.chunk_size)

        failed = False
        connection = mail.get_connection()
        connection.open()
        for i in range(0, count, self.chunk_size):
            recipients_chunk = self._get_recipients_chunk(i)
            message_list = self._create_messages(recipients_chunk)

            try:
                self._send_message_chunk(message_list, connection)
                self._update_chunk_status(recipients_chunk)
                self._notify()
            except smtplib.SMTPException as exc:
                self._update_chunk_error(send_failed, i, recipients_chunk, exc)
                failed = True
            except ConnectionRefusedError as exc:
                self._update_chunk_error(
                    send_failed, i,  recipients_chunk, exc)
                failed = True

        connection.close()
        self._clean_recipients()
        self._clean_send_failed(send_failed, failed)
        self._finalize(failed)
        self._notify()

    def _notify(self):
        if self.notify_callback:
            self.notify_callback(self.email_batch)

    def _update_batch(self):
        self.email_batch.status = models.EmailBatchMessage.Status.PROCESSING
        self.email_batch.save()

    def get_or_create_send_failed(self, chunk_size):
        """
        Group email batch recipients which sent has failed
        If there is no fail, this record is deleted
        """
        # pylint: disable=no-member
        send_failed, _created = models.EmailSendFailed.objects.get_or_create(
            email_batch=self.email_batch,
            defaults={'error_message': 'Chunk size: ' + str(chunk_size) + '\n'}
        )
        return send_failed

    def create_recipients(self, users_pk):
        """
        Create the recipients list batch in database to be sent
        """
        recipient_list = []
        for user_pk in users_pk:
            recipient_list.append(
                models.EmailBatchRecipient(
                    user_id=user_pk, email_batch=self.email_batch)
            )
        # pylint: disable=no-member
        models.EmailBatchRecipient.objects.bulk_create(recipient_list)

        # Bulk create return a list of objects without pk (if pk is autofield),
        #  so it should be retrived from database
        self.load_recipients()

        return len(self.recipients)

    def load_recipients(self):
        """
        Load the recipients list batch in database to be sent
        """
        # pylint: disable=no-member
        self.recipients = models.EmailBatchRecipient.objects.filter(
            email_batch=self.email_batch).annotate(address=F('user__email'))

        return len(self.recipients)

    def _get_recipients_chunk(self, i):
        recipients_chunk = self.recipients[i:i+self.chunk_size]
        return recipients_chunk

    def _create_messages(self, recipients_chunk):
        """
        Create the message list from chunk
        """
        message_list = []
        for recipient in recipients_chunk:
            msg = mail.EmailMessage(
                self.subject, self.message, to=[recipient.address])
            msg.content_subtype = "html"
            message_list.append(msg)
        return message_list

    def _send_message_chunk(self, message_list, connection):
        """
        Send recipient list messages in chunks for chunk_size
        """
        sent_count = connection.send_messages(message_list)
        self.email_batch.sent += sent_count
        self.email_batch.save()

    def _update_chunk_status(self, recipients_chunk):
        """
        Set sent field of email bath recipient to true to indicate email sent success
        Succeeded sendings records will be deleted
        Faile sending recipients are kept to debug or future resendind
        """
        # pylint: disable=no-member
        for recipient in recipients_chunk:
            recipient.sent = True
        models.EmailBatchRecipient.objects.bulk_update(
            recipients_chunk, ['sent'])

    def _update_chunk_error(self, send_failed, chunk, recipients_chunk, exc):
        send_failed.error_message += f"{str(exc)} - chunk: {chunk};\n"
        send_failed.save()
        # pylint: disable=no-member
        for recipient in recipients_chunk:
            recipient.email_send_failed = send_failed
            recipient.error_message = str(exc)
        models.EmailBatchRecipient.objects.bulk_update(
            recipients_chunk, ['email_send_failed', 'error_message'])

    def _clean_recipients(self):
        # Delete all send recipient
        # pylint: disable=no-member
        sent = models.EmailBatchRecipient.objects.filter(
            email_batch=self.email_batch, sent=True)
        sent.delete()

    def _clean_send_failed(self, send_failed, failed):
        # Delete send_failed
        if not failed:
            send_failed.delete()

    def _finalize(self, failed):
        status = models.EmailBatchMessage.Status
        self.email_batch.status = status.FINISHED_ERR if failed else status.FINISHED
        self.email_batch.date_finished = timezone.localtime(timezone.now())
        self.email_batch.save()
