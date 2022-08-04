"""
Core models
"""


from allauth.account.models import EmailAddress
from django.conf import settings
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from tinymce import models as tinymce_models

from accounts import models as accounts_models
from accounts import roles


class CoreUserManager(UserManager):
    """
    Create a superuser with ADMIN role and an
    account email to avoid email verification.
    """

    def create_superuser(self, *args, **kwargs):
        user = super().create_superuser(*args, **kwargs)
        roles.create_user_role(user, roles.Roles.ADMIN)
        EmailAddress.objects.create(
            user=user,
            email=user.email,
            verified=True,
            primary=True
        )
        return user


class User(AbstractUser):
    """
    User customization
    """

    objects = CoreUserManager()

    def __str__(self) -> str:
        return f'{self.get_full_name()} - {self.email}'


class AcceptanceTerm(models.Model):
    """
    Platform accepance term
    """

    class Meta:
        """
        Meta class
        """
        verbose_name = 'Termo de aceite'
        verbose_name_plural = 'Termos de aceite'

        constraints = [
            models.UniqueConstraint(
                fields=['type', 'version'], name='unique_term_version')
        ]

    class Type(models.TextChoices):
        """
        Acceptance term type
        SIGNUP AND PRIVACY_POLICY are required.
        OTHER are additional terms
        """
        SIGNUP = 'SIG', 'Uso da plataforma'
        PRIVACY_POLICY = 'PPO', 'Política de provacidade'

    title = models.CharField(max_length=256, verbose_name='Título')
    type = models.CharField(
        max_length=3, verbose_name='Tipo de termo', choices=Type.choices)
    text = tinymce_models.HTMLField(verbose_name='Texto to termo')
    date_created = models.DateTimeField(
        verbose_name='Data de criação', auto_now_add=True)
    date_changed = models.DateTimeField(
        verbose_name='Última atualização', auto_now=True, editable=False)
    is_active = models.BooleanField(verbose_name='Ativo', default=True)

    annotation = models.TextField(
        verbose_name="Anotações", null=True, blank=True)

    version = models.PositiveIntegerField(verbose_name="Versão")

    # pylint: disable=no-member
    def __str__(self) -> str:
        return f'{self.get_type_display()}- versão: {self.version} - {self.title} -  ativo: {"sim" if self.is_active else "não" }'

    def save(self, *args, **kwargs):
        # Only one for any type must be active
        if self.is_active:
            actives = AcceptanceTerm.objects.filter(
                is_active=True, type=self.type)
            if actives:
                actives.update(is_active=False)
        super().save(*args, **kwargs)


class UserAcceptanceTerm(models.Model):
    """
    User acceptance term
    """

    class Meta:
        """
        Meta class
        """

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             verbose_name='Usuário', on_delete=models.CASCADE)
    term = models.ForeignKey(
        AcceptanceTerm, verbose_name='Term de aceite', on_delete=models.CASCADE)
    acceptance_date = models.DateTimeField(
        verbose_name='Data de aceitação', auto_now_add=True)
    date_cancelled = models.DateTimeField(
        verbose_name='Cancelamento', null=True, blank=True, editable=False)

    # pylint: disable=no-member
    def __str__(self) -> str:
        return f'{self.user.email} - {self.term.title}- {self.acceptance_date}'


class EmailBatchMessage(accounts_models.RoleModelMixin):
    """
    Generic batch message for a group of users
    """
    class Meta:
        """
        Meta class
        """
        verbose_name = 'Lote de email'
        verbose_name_plural = 'Lotes de emails'

    class Status(models.TextChoices):
        """
        Status
        """
        FINISHED = 'FINI', 'Finalizado'
        FINISHED_ERR = 'FERR', 'Finalizado com erro'
        PROCESSING = 'PROC', 'Processando'
        WAITING = 'WAIT', 'Aguardando'

    subject = models.CharField(
        verbose_name='Assunto', max_length=256, null=True, blank=True)
    message = tinymce_models.HTMLField(verbose_name='Mensagem')
    status = models.CharField(verbose_name='Situação', max_length=4,
                              choices=Status.choices, default=Status.WAITING)
    sent = models.PositiveIntegerField(verbose_name='Enviados', default=0)
    total = models.PositiveIntegerField(verbose_name='Total', default=0)
    date_created = models.DateTimeField(
        verbose_name='Data de criação', auto_now_add=True)
    date_finished = models.DateTimeField(
        verbose_name='Data de finalização', null=True, blank=True)
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name='Operador', on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.pk} -{self.subject} - {self.role} - {self.date_created}"


class EmailSendFailed(models.Model):
    """
    Store sending fail
    """
    class Meta:
        """
        Meta class
        """
        verbose_name = 'Falha de envio de email'
        verbose_name_plural = 'Falhas de envio de email'

    email_batch = models.ForeignKey(
        EmailBatchMessage, on_delete=models.CASCADE)
    date_created = models.DateTimeField(
        verbose_name='Data de criação', auto_now_add=True)
    error_message = models.TextField()

    def __str__(self) -> str:
        return f"{self.pk} - {self.date_created} - {self.email_batch}"


class EmailBatchRecipient(models.Model):
    """
    Stores email address to send temporarely
    The entry is removed after sending email
    """
    class Meta:
        """
        Meta class
        """
        verbose_name = 'Email agendado'
        verbose_name_plural = 'Emails agendados'

    email_batch = models.ForeignKey(
        EmailBatchMessage, verbose_name='Lote de envio', on_delete=models.CASCADE)
    email_send_failed = models.ForeignKey(
        EmailSendFailed, verbose_name='Lote de falha de envio', on_delete=models.CASCADE,
        null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             verbose_name='Usuário', on_delete=models.CASCADE)
    sent = models.BooleanField(verbose_name='Enviado', default=False)
    error_message = models.TextField(
        verbose_name='Mensagem de erro', null=True, blank=True)

    def __str__(self) -> str:
        # pylint: disable=no-member
        return f"{self.pk} - {self.email_batch} - {self.user.email}"


class Company(models.Model):
    """
    Company data
    """

    class Meta:
        """
        Meta class
        """
        verbose_name = 'Dados da empresa'
        verbose_name_plural = 'Dados das empresas'

    class AboutUsBkgColor(models.TextChoices):
        """
        About us background color
        """

        BLACK = '#000000', 'Preto'
        WHITE = '#FFFFFF', 'Branco'
        LIGHT_GREY = '#F8F9FA', 'Cinza claro'

    name = models.CharField(max_length=256, verbose_name="Nome da empresa")

    logo = models.ImageField(verbose_name='Logo da empresa (ícone)',
                             null=True, blank=True, upload_to='public/')

    name_logo = models.ImageField(verbose_name='Logo do nome (menu)',
                                  null=True, blank=True, upload_to='public/')

    cnpj = models.CharField(max_length=20, verbose_name='CNPJ')

    support_phone = models.CharField(
        max_length=15, verbose_name='Telefone de atendimento', null=True, blank=True)

    contact_email = models.EmailField(
        verbose_name="Email de contato", null=True, blank=True)

    support_email = models.EmailField(
        verbose_name="Email de atendimento", null=True, blank=True)

    disclaimer = models.CharField(
        max_length=1024, verbose_name="Disclaimer",
        help_text="Máximo de 1024 caracteres",
        null=True, blank=True)

    fix_disclaimer_end = models.BooleanField(
        verbose_name='Fixar disclaimer no final da página',
        help_text='Por padrão o disclaimer é sempre visível',
        default=False
    )

    about_us = tinymce_models.HTMLField(
        verbose_name='Sobre a empresa',
        help_text="Mostrado na página pública",
        null=True, blank=True,
    )

    abt_us_signup_btn = models.CharField(
        max_length=50,
        verbose_name='Texto do botão criar conta',
        help_text="Botão mostrado na caixa 'Sobre a empresa'",
        default='Abrir uma conta'
    )

    abt_us_bkg_color = models.CharField(
        max_length=7,
        verbose_name="Cor de fundo",
        help_text="Cor da caixa 'Sobre a empresa'",
        choices=AboutUsBkgColor.choices,
        default=AboutUsBkgColor.BLACK,
    )

    bank_name = models.CharField(
        verbose_name='Nome do banco', max_length=255, null=True, blank=True)
    bank_code = models.IntegerField(
        verbose_name='Código do banco', null=True, blank=True)
    bank_ispb = models.IntegerField(
        verbose_name='ISPB', null=True, blank=True)

    bank_branch_number = models.IntegerField(
        verbose_name='Agência', null=True, blank=True)
    bank_branch_digit = models.CharField(
        verbose_name='Dígito da agência', max_length=1, null=True, blank=True)
    account_number = models.IntegerField(
        verbose_name='Número da conta', null=True, blank=True)
    account_digit = models.IntegerField(
        verbose_name='Dígito da conta', null=True, blank=True)

    facebook_link = models.CharField(
        max_length=512, verbose_name='Facebook', null=True, blank=True)

    linkedin_link = models.CharField(
        max_length=512, verbose_name='Linkedin', null=True, blank=True)

    instagram_link = models.CharField(
        max_length=512, verbose_name='Instagram', null=True, blank=True)

    @property
    def facebook_url(self):
        """
        Facebook url
        """
        return 'https://facebook.com/' + str(self.facebook_link).strip()

    @property
    def linkedin_url(self):
        """
        Linkedin url
        """
        return 'https://linkedin.com/' + str(self.linkedin_link).strip()

    @property
    def instagram_url(self):
        """
        Instagram url
        """
        return 'https://instagram.com/' + str(self.instagram_link).strip()


    @property
    def about_us_colors(self):
        """
        Helpre function to get colors
        """
        color = self.AboutUsBkgColor.BLACK

        if self.abt_us_bkg_color == self.AboutUsBkgColor.BLACK:
            color = self.AboutUsBkgColor.WHITE

        return {
            'background_color': self.abt_us_bkg_color,
            'color': color
        }

    @ property
    def bank(self):
        """ Bank """
        return f'{self.bank_code} - {self.bank_name}'

    @ property
    def bank_branch(self):
        """ Bank branch """
        if self.bank_branch_digit:
            return f'{self.bank_branch_number} - {self.bank_branch_digit}'
        else:
            return f'{self.bank_branch_number}'

    @ property
    def bank_account(self):
        """ Bank account """
        if self.account_digit:
            return f'{self.account_number} - {self.account_digit}'
        else:
            return f'{self.account_number}'

    def __str__(self) -> str:
        return f'{self.name} - {self.cnpj} - email:{self.contact_email}'


class WorkflowTask(models.Model):
    """
    Generic admin task table
    """

    class Meta:
        """
        Meta class
        """
        verbose_name = "Tarefa"
        verbose_name_plural = "Tarefas"

    name = models.CharField(max_length=256, verbose_name='Nome da tarefa')

    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name='operador',
        on_delete=models.CASCADE, related_name='workflowtask_operator')

    evaluator = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name='avaliador',
        on_delete=models.CASCADE, related_name='workflowtask_evaluator',
        null=True, blank=True, editable=False)

    register_id = models.IntegerField(verbose_name='Id do registro')
    form_view = models.CharField(
        max_length=256, verbose_name='View do formulário')

    history_model = models.CharField(
        max_length=256, verbose_name='Modelo do histórico do registro', null=True, blank=True)
    history_id = models.IntegerField(
        verbose_name='Id do histórico do registro', null=True, blank=True)

    date_created = models.DateTimeField(
        verbose_name='Criação', auto_now_add=True)
    date_verified = models.DateTimeField(
        verbose_name='Verificação', null=True, blank=True)

    status = models.CharField(max_length=64, verbose_name='Situação')

    @ property
    def verified(self):
        """
        Returns if task was verified
        """
        return self.date_verified is not None


class FAQConfig(models.Model):
    """
    FAQ page configurations
    """
    class Meta:
        """
        Meta class
        """
        constraints = [
            models.UniqueConstraint(
                fields=['target_page'], name='unique_faq_config_constraint')
        ]

    class Page(models.TextChoices):
        """
        Page choices
        """
        PUBLIC = 'PUB', 'Pública'
        CLIENT = 'CLI', 'Cliente'

    title = models.CharField(max_length=128, verbose_name='Título da página')

    target_page = models.CharField(
        max_length=3, verbose_name='Página', choices=Page.choices, null=True, blank=True)

    @staticmethod
    def get_faq(target_page: Page):
        """
        FAQ query objects list based on target page
        """
        # pylint: disable=no-member
        try:
            obj = FAQConfig.objects.get(target_page=target_page)
            return {
                'title': obj.title,
                'objects': obj.faq_set.all()
            }
        except FAQConfig.DoesNotExist:
            return None

    def __str__(self):
        if self.target_page:
            return self.Page(self.target_page).label
        return '-----'


class FAQ(models.Model):
    """
    Questions and Answers
    """
    faq_config = models.ManyToManyField(
        FAQConfig, verbose_name='Página de exibição', blank=True)
    question = models.CharField(max_length=1024, verbose_name='Questão')
    answer = tinymce_models.HTMLField(verbose_name='Resposta')
    order = models.PositiveIntegerField(verbose_name='Ordem de exibição')

    def __str__(self):
        return str(self.question)
