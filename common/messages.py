"""
Restrict messages to show
"""

from django.contrib import messages as _messages
from django.contrib.messages import constants


__messages = {
    constants.SUCCESS :_messages.success,
    constants.INFO :_messages.info,
    constants.WARNING :_messages.warning,
    constants.DEBUG :_messages.debug,
    constants.ERROR :_messages.error,
}

def message_add(request, message, message_type=constants.SUCCESS):
    """
    Show only messages with core extra_tag, see template common/messages.html
    This avoids show messages from another packajages as django-allauth
    """
    __messages[message_type](request, message, extra_tags='core')


def message_modal_add(request, context, title, message, message_type=constants.SUCCESS):
    """
    Show only messages with core extra_tag, see template common/messages.html
    This avoids show messages from another packajages as django-allauth
    """
    context['message'] = {
        'title': title,
        'show': 'show'
    }
    __messages[message_type](request, message, extra_tags='core_modal')
