"""
Email message logging config
"""

import logging

from django.core import mail
from django.core.mail import get_connection

from django_db_logger.config import DJANGO_DB_LOGGER_ENABLE_FORMATTER
from django_db_logger.db_log_handler import DatabaseLogHandler

db_default_formatter = logging.Formatter()


class DatabaseEmailReporter(DatabaseLogHandler):
    """
    Customize exception reporting to save log in database and sending email
    """

    def __init__(self, email_backend=None):
        super().__init__()
        self.email_backend = email_backend

    def emit(self, record):

        #pylint: disable=import-outside-toplevel
        from django_db_logger.models import StatusLog

        trace = None

        if record.exc_info:
            trace = db_default_formatter.formatException(record.exc_info)

        if DJANGO_DB_LOGGER_ENABLE_FORMATTER:
            msg = self.format(record)
        else:
            msg = record.getMessage()

        kwargs = {
            'logger_name': record.name,
            'level': record.levelno,
            'msg': msg,
            'trace': trace
        }

        # pylint: disable=no-member
        obj = StatusLog.objects.create(**kwargs)

        subject = f'id[{obj.id}] - {obj.get_level_display()} - {msg}'

        if trace:
            message = f'logger: {record.name}\nmessage: {msg}\ntrace: {trace}'
        else:
            message = f'logger: {record.name}\nmessage: {msg}'

        self._send_mail(subject,
                        message,
                        html_message=None)

    def _send_mail(self, subject, message, *args, **kwargs):
        mail.mail_admins(subject, message, *args,
                         connection=self._connection(), **kwargs)

    def _connection(self):
        return get_connection(backend=self.email_backend, fail_silently=True)
