"""
Helper methods to handle roles
"""

# Load Invitations from models. Loadin from .invitations causes error
# as the model aren't loaded yet.
from .models import UserRole, Roles, CustomInvitation as Invitation

# TODO log undefined role?


def create_user_role(user, role):
    """
    Create a user role
    """
    # pylint: disable=no-member
    return UserRole.objects.create(user=user, role=role)


def has_role(user, role):
    """
    Check if user has role
    """
    # pylint: disable=no-member
    return UserRole.objects.filter(user=user, role=role).exists()


def has_role_in(user, role_list):
    """
    Check if user has role
    """
    # pylint: disable=no-member
    return UserRole.objects.filter(user=user, role__in=role_list).exists()


def has_active_invitation(email):
    """
    Check if user has active invitation
    """
    # pylint: disable=no-member
    invitation = Invitation.objects.filter(email=email).last()
    if invitation:
        if not invitation.key_expired() and not invitation.accepted:
            return invitation.role
    return None


def get_role_from_invitation(user):
    """
    Get role from last invitation sent
    """
    invitation = Invitation.objects.filter(email=user.email).last()
    if invitation:
        if not invitation.key_expired():
            return invitation.role
    return Roles.UNDEF


def create_user_role_from_invitation(user):
    """
    Create user role got form invitation
    If there is no invitation, create an UNDEF role
    """
    role = get_role_from_invitation(user)
    return create_user_role(user, role)


def get_role_from_invitation_email(email):
    """
    Get role from last invitation for the given email
    """
    invitation = Invitation.objects.filter(email=email).last()
    if invitation:
        if not invitation.key_expired() and not invitation.accepted:
            return invitation.role
    return Roles.UNDEF


def get_last_role(user):
    """
    Get user last registered role
    """
    # pylint: disable=no-member
    user_role = UserRole.objects.filter(user=user).last()
    if user_role.role:
        return user_role.role
    return None


def get_last_user_role(user):
    """
    Get user last registered role
    """
    # pylint: disable=no-member
    user_role = UserRole.objects.filter(user=user).last()
    return user_role
