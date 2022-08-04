"""
Core signals
"""

from allauth.account.signals import user_signed_up
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts import roles, models


@receiver(post_save, sender=User)
#pylint: disable=unused-argument
def skip_email_confirmation(sender, instance, created, **kwargs):
    """
    Skip email confirmation if a admin is created
    """
    if created and instance.is_superuser:
        try:
            # pylint: disable=import-outside-toplevel
            from allauth.account.models import EmailAddress
            EmailAddress.objects.create(
                email=instance.email,
                verified=True,
                primary=True,
                user=instance
            )
        # pylint: disable=broad-except
        except Exception:
            pass


@receiver(user_signed_up)
#pylint: disable=unused-argument
def finish_signup(sender, **kwargs):
    """
    User settings after signup
    """
    user = kwargs['user']
    
    # Set admin status after signup
    if roles.has_role(user, roles.Roles.ADMIN):
        user.is_superuser = True
        user.is_staff = True
        user.save()

    # Creates user default profile
    if not getattr(user, 'userprofile', None):
        # pylint: disable=no-member
        models.UserProfile.objects.create(user=user)
