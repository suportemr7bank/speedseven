"""
Client models
"""

from allauth.account.models import EmailAddress
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models
from simple_history.models import HistoricalRecords

from accounts import roles as account_roles
from core import workflow

def upload_rg_cnh(instance, filename):
    """
    RG / CNH Upload folder
    """
    return f'private/uploads/clients/{instance.pk}/rc_{filename}'


def upload_company_agreement(instance, filename):
    """
    Company aggrement/ CNH upload folder
    """
    return f'private/uploads/clients/{instance.pk}/ca_{filename}'


def upload_address_proof(instance, filename):
    """
    Adress proof upload folder
    """
    return f'private/uploads/clients/{instance.pk}/ap_{filename}'


class ClientBase(workflow.ApprovalWorkflow):
    """
    Client base model
    """

    class Meta:
        """
        Meta class
        """
        abstract = True

    class Type(models.TextChoices):
        """
        Client type
        """
        PF = 'PF', 'Pessoa física'
        PJ = 'PJ', "Pessoa jurídica"

    class States(models.TextChoices):
        """
        States
        """
        AC = 'AC', 'Acre'
        AL = 'AL', 'Alagoas'
        AM = 'AM', 'Amazônia'
        BA = 'BA', 'Bahia'
        CE = 'CE', 'Ceará'
        DF = 'DF', 'Distrito Federal'
        ES = 'ES', 'Espirito Santo'
        GO = 'GO', 'Goiás'
        MA = 'MA', 'Maranhão'
        MG = 'MG', 'Minas Gerais'
        MS = 'MS', 'Mato Grosso do Sul'
        MT = 'MT', 'Mato Grosso'
        PB = 'PB', 'Paraíba'
        PE = 'PE', 'Permanbuco'
        PI = 'PI', 'Piauí'
        PR = 'PR', 'Paraná'
        RJ = 'RJ', 'Rio de Janeiro'
        RN = 'RN', 'Rio Grande do Norte'
        RO = 'RO', 'Rondônia'
        RR = 'RR', 'Rorâima'
        RS = 'RS', 'Rio Grande do Sul'
        SC = 'SC', 'Santa Catarina'
        SE = 'SE', 'Sergipe'
        SP = 'SP', 'São Paulo'


    first_name = models.CharField(verbose_name='Nome', max_length=150)

    last_name = models.CharField(verbose_name='Sobrenome', max_length=150)

    type = models.CharField(
        max_length=2, verbose_name='Pessoa física/jurídica', choices=Type.choices, default=Type.PF)
    birth_date = models.DateField(
        verbose_name='Data de nascimento', null=True, blank=True)
    cpf = models.CharField(
        max_length=14, verbose_name='CPF', null=True, blank=True)
    cnpj = models.CharField(
        max_length=20, verbose_name='CNPJ', null=True, blank=True)
    company_name = models.CharField(
        max_length=256, verbose_name='Nome da empresa', null=True, blank=True)
    phone = models.CharField(
        max_length=15, verbose_name='Telefone', null=True, blank=True)
    address = models.CharField(
        max_length=256, verbose_name='Endereço', null=True, blank=True)
    number = models.CharField(
        max_length=10, verbose_name='Número', null=True, blank=True)
    complement = models.CharField(
        max_length=64, verbose_name='Complemento', null=True, blank=True)
    zip_code = models.CharField(
        max_length=9, verbose_name='Cep', null=True, blank=True)
    city = models.CharField(
        max_length=128, verbose_name='Cidade', null=True, blank=True)
    state = models.CharField(
        max_length=2, verbose_name='Estado', choices=States.choices, null=True, blank=True)

    politically_exposed = models.BooleanField(
        verbose_name='Pessoa politicamente exposta', default=False)

    rg_cnh = models.FileField(
        verbose_name='RG/CNH',
        upload_to=upload_rg_cnh,
        validators=[FileExtensionValidator(['png', 'jpeg', 'jpg', 'pdf'])],
        null=True,
        blank=True)

    company_agreement = models.FileField(
        verbose_name='Contrato social',
        upload_to=upload_company_agreement,
        validators=[FileExtensionValidator(['png', 'jpeg', 'jpg', 'pdf'])],
        null=True,
        blank=True)

    address_proof = models.FileField(
        verbose_name='Comprovante de endereço',
        upload_to=upload_address_proof,
        validators=[FileExtensionValidator(['png', 'jpeg', 'jpg', 'pdf'])],
        null=True,
        blank=True)

    date_created = models.DateTimeField(
        verbose_name='Criação', auto_now_add=True)


class Client(ClientBase):

    """
    Client model
    """

    class Meta:
        """
        Meta class
        """
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

    task_name = 'Aprovação de cadastro de cliente'
    form_view = 'core:client_update'


    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    history = HistoricalRecords()

    @property
    def registration_completed(self):
        """
        Indicate if registration is completed
        """
        #pylint: disable=no-member
        items = [
            self.user.first_name,
            self.user.last_name,
            self.cpf,
            self.phone,
            self.birth_date,
            self.address,
            self.city,
            self.state,
            self.rg_cnh.name,
            self.address_proof.name
        ]

        if self.type == self.Type.PJ:
            items.append(self.company_agreement.name)

        return None not in items and '' not in items

    @classmethod
    def required_fields(cls, client_type):
        """
        Required fields list for cpf
        """
        required = [
            'phone',
            'birth_date',
            'address',
            'city',
            'state',
            'rg_cnh',
            'address_proof'
        ]

        if client_type == cls.Type.PF:
            required.append('cpf')
        else:
            required += ['cpf', 'cnpj', 'company_name', 'company_agreement', ]

        return required

    @classmethod
    def create_client(cls, user, **data):
        """
        Create client with appropriate role without sendind mail confirmation.
        This may be used for creating client in admin panel o by api, when
        email confirmation is not necessary.
        """
        cls.set_role_and_email(user)
        # pylint: disable=no-member
        client = Client.objects.create(user=user, **data)
        return client

    @classmethod
    def set_role_and_email(cls, user):
        """
        Set appropriate role and an verified email
        """
        cls._create_email_address(user)
        cls._create_role(user)

    @classmethod
    def _create_email_address(cls, user):
        """
        Necessary to prevent django allauth requesting email confirmation
        """
        EmailAddress.objects.create(
            user=user,
            email=user.email,
            verified=True,
            primary=True
        )

    @classmethod
    def _create_role(cls, user):
        """
        The client must have a client role
        """
        account_roles.create_user_role(user, account_roles.Roles.CLIENT)

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def __str__(self) -> str:
        # pylint: disable=no-member
        return f'{self.user.get_full_name()} - {self.user.email}'
