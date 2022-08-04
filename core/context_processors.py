"""
Core context processors
"""

from .models import Company


def site_name_logo_url(request):
    """
    Name logo url
    """
    #pylint: disable=no-member
    company = Company.objects.last()
    url = None
    if company and company.name_logo:
        url = company.name_logo.url

    return {'site_name_logo_url': url}
