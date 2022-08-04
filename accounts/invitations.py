"""
Module do isolate invitations

In case Invitation model must be replaced, write a new invitation model or an adapter.

"""
from invitations.utils import get_invitation_model as __get_invitation_model
from scheduler.background import BackgroundTask
Invitation = __get_invitation_model()


class SendInivitationMixin:
    """
    Mixin for sending infitation
    """
    def send_invitation(self, invitation):
        """
        Send invitation in background task
        """

        invitation.error_message = None
        invitation.sent = None
        invitation.expiration_date = None
        invitation.save()

        BackgroundTask.exec_callable(
            invitation.send_invitation, request=self.request)


class CreateInivitationMixin(SendInivitationMixin):
    """
    Mixin for create and send invitation
    """

    def create_invitation(self, email, inviter, role):
        """
        Create invitation
        """
        return Invitation.create(email=email, inviter=inviter, role=role)

    def form_valid(self, form):
        """
        Create and send an invitation
        """
        email = form.cleaned_data['email']
        role = form.cleaned_data['role']
        invitation = self.create_invitation(email, self.request.user, role)
        self.send_invitation(invitation)
        return super().form_valid(form)
