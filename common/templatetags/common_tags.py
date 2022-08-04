from django import template
from django.urls import reverse

register = template.Library()


@register.simple_tag(takes_context=True)
def abs_url(context, view_name, *args, **kwargs):
    """
    reverse absolute url

    Workaround - Azure webapp
    request.build_absolute_uri builds an url with http schema not https

    if not request.is_secure():
        scheme = request.scheme if settings.DEBUG else request.scheme + 's'
    return f'{scheme}://{request.get_host()}{reverse(view_name, args=args, kwargs=kwargs)}'
    """

    request = context['request']
    return request.build_absolute_uri(reverse(view_name, args=args, kwargs=kwargs))
