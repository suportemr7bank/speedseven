"""
Accounts models
"""

import datetime

from django.conf import settings
from django.contrib.sites.models import Site
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string

from invitations import signals
from invitations.adapters import get_invitations_adapter
from invitations.app_settings import app_settings
from invitations.base_invitation import AbstractBaseInvitation

try:
    from constance import config

    def _get_invitation_expiry():
        return getattr(config, 'ACCOUNT_INVITATION_EXPIRY', app_settings.INVITATION_EXPIRY)
except ImportError:
    def _get_invitation_expiry():
        return app_settings.INVITATION_EXPIRY


class Roles(models.TextChoices):
    """
    Platform role
    """
    ADMIN = 'ADMIN', 'Administrador'
    CLIENT = 'CLIENT', 'Cliente'
    BROKER = 'BROKER', 'Gerente de conta'
    APIACC = 'APIACC', 'Acesso à página da API'

    # Must be the last two (don't change order)
    APIAPP = 'APIAPP', 'Acesso à API'
    UNDEF = 'UNDEF', 'Indefinido'


class RoleModelMixin(models.Model):
    """
    Mixin form role
    """
    class Meta:
        """
        Meta class
        """
        abstract = True

    role = models.CharField(max_length=6, verbose_name='Papel', choices=Roles.choices)


class CustomInvitation(RoleModelMixin, AbstractBaseInvitation):
    """
    CustomInvitation model
    """

    email = models.EmailField(unique=True, verbose_name='Email',
                              max_length=app_settings.EMAIL_MAX_LENGTH)

    created = models.DateTimeField(verbose_name='created',
                                   auto_now_add=True)

    expiration_date = models.DateTimeField(
        verbose_name=('Vencimento'), null=True, blank=True)

    error_message = models.TextField(
        verbose_name='Mensagem de erro', null=True, blank=True)

    @classmethod
    def create(cls, email, inviter=None, **kwargs):
        key = get_random_string(64).lower()
        instance = cls._default_manager.create(
            email=email,
            key=key,
            inviter=inviter,
            **kwargs)
        return instance

    def _send_invitation(self, request, **kwargs):
        current_site = kwargs.pop('site', Site.objects.get_current())
        invite_url = reverse('invitations:accept-invite',
                             args=[self.key])
        invite_url = request.build_absolute_uri(invite_url)
        ctx = kwargs
        ctx.update({
            'invite_url': invite_url,
            'site_name': current_site.name,
            'email': self.email,
            'key': self.key,
            'inviter': self.inviter,
        })

        email_template = 'invitations/email/email_invite'

        get_invitations_adapter().send_mail(
            email_template,
            self.email,
            ctx)
        self.sent = timezone.now()
        self.save()

        signals.invite_url_sent.send(
            sender=self.__class__,
            instance=self,
            invite_url_sent=invite_url,
            inviter=self.inviter)

    def key_expired(self):
        if self.expiration_date:
            return self.expiration_date < timezone.now()
        else:
            return False

    def send_invitation(self, request, **kwargs):
        try:
            self._send_invitation(request, **kwargs)
            self.expiration_date = (
                self.sent + datetime.timedelta(days=_get_invitation_expiry()))
        except Exception as err:
            self.error_message = str(err)
        self.save()

    def __str__(self):
        return f'Invite: {self.email}'


class UserRole(RoleModelMixin):
    """
    User role
    """
    class Meta:
        """
        Meta class
        """
        verbose_name = 'Papel do usuário'
        verbose_name_plural = 'Papéis dos usuários'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'role'], name='unique_user_role_constraint')
        ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)

    def __str__(self) -> str:
        # pylint: disable=no-member
        return f'{self.user.email} - {self.role}'


class ApiAccess(models.Model):
    """
    Api alloewd access
    """
    class Meta:
        """
        Meta class
        """
        verbose_name = "Acesso à API"
        verbose_name_plural = "Acessos à API"

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             verbose_name='Usuário e senha de acesso',
                             on_delete=models.CASCADE)

    access_key = models.CharField(
        verbose_name='Senha/Chave de acess', max_length=128)

    date_created = models.DateTimeField(
        verbose_name='Data de criação',
        auto_now_add=True, editable=False)

    is_active = models.BooleanField(verbose_name='Ativo')

    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name='Operador',
        related_name='user_operator', on_delete=models.CASCADE, editable=False)


class UserProfile(models.Model):
    """
    User settings and profile
    """

    class Theme(models.TextChoices):
        """
        Site theme for user
        """
        DARK = 'dark', 'Tema escuro'
        LIGHT = 'light', 'Tema claro'

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, verbose_name='Usuário', on_delete=models.CASCADE)

    theme = models.CharField(
        max_length=5, verbose_name='Tema', choices=Theme.choices, default=Theme.DARK)
