"""
Client signals
"""

from django.dispatch import receiver
from allauth.account.signals import user_signed_up

from accounts import roles as accounts_roles
from core import models as core_models

from .models import Client


@receiver(user_signed_up)
#pylint: disable=unused-argument
def create_client(sender, **kwargs):
    """
    Create a client after signup
    """
    user = kwargs['user']
    if accounts_roles.has_role(user, accounts_roles.Roles.CLIENT):
        account_type = kwargs['form_data']['account_type']
        cpf = kwargs['form_data']['cpf']
        first_name = kwargs['form_data']['first_name']
        last_name = kwargs['form_data']['last_name']
        data = {
            'user': user,
            'type': account_type,
            'cpf': cpf,
            'first_name': first_name,
            'last_name': last_name 
        }

        # pylint: disable=no-member
        Client.objects.create(operator=user, **data)

        # pylint: disable=no-member
        core_models.UserAcceptanceTerm.objects.create(
            user=user,
            term=core_models.AcceptanceTerm.objects.filter(
                type=core_models.AcceptanceTerm.Type.SIGNUP, is_active=True).last()
        )
