"""
Accounts models
"""

from django.db import models
from tinymce import models as tinymce_models

from .app_config import TEMPLATE_ABSOLUTE_FOLDER, TEMPLATE_FOLDER


class EmailTemplate(models.Model):
    """
    Templates for application emails
    The view save template in a file in email templates folder
    """
    FILE_HTML = 'html'
    FILE_TXT = 'txt'

    FILE_TYPE = [
        (FILE_HTML, 'html'),
        (FILE_TXT, 'txt'),
    ]

    class Meta:
        """
        Meta data
        """
        verbose_name = 'Modelo de email'
        verbose_name_plural = 'Modelos de email'
        constraints = [
            models.UniqueConstraint(
                fields=['prefix'], name='unique_template')
        ]

    type = models.CharField(max_length=64, verbose_name="Tipo de email")

    prefix = models.CharField(max_length=256, verbose_name='Prefixo',
                              help_text="Prexixo do caminho relativo do arguivo "
                                        "Ex: invitations/email/email_invite")

    subject_template = models.CharField(
        max_length=128, verbose_name='Assunto', null=True, blank=True)

    subject_tags = models.TextField(
        verbose_name='Descrição das tags do assunto', null=True, blank=True)

    text_template = models.TextField(verbose_name='Mensagem em texto puro')

    message_template = tinymce_models.HTMLField(
        verbose_name='Mensagem em rich text')

    message_tags = models.TextField(
        verbose_name='Descrição das tags do modelo', null=True, blank=True)

    date_created = models.DateTimeField(
        verbose_name='Data de criação', auto_now_add=True, editable=False)
    date_modified = models.DateTimeField(
        verbose_name='Última modificação', auto_now=True, editable=False)

    write_error = models.CharField(
        max_length=256, null=True, blank=True, editable=False)

    @property
    def subject_path(self):
        """
        Subject template file path
        """
        return TEMPLATE_FOLDER + self.prefix + '_subject.txt'

    @property
    def message_path(self):
        """
        Message template file path
        """
        return TEMPLATE_FOLDER + self.prefix + '_message.html'

    @property
    def text_path(self):
        """
        Message template file path
        """
        return TEMPLATE_FOLDER + self.prefix + '_message.txt'

    @staticmethod
    def create_paths(prefix):
        """
        Create default email template paths
        """
        subject_path = TEMPLATE_ABSOLUTE_FOLDER + (prefix + '_subject.txt')
        message_path = TEMPLATE_ABSOLUTE_FOLDER + (prefix + '_message.html')
        text_path = TEMPLATE_ABSOLUTE_FOLDER + (prefix + '_message.txt')
        return subject_path, message_path, text_path

    def __str__(self) -> str:
        #pylint: disable=no-member
        return f'{self.type.get_type_display()} - {self.file_name}'
