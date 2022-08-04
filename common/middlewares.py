"""
Page content request middleware
"""
from constance import config

class PageContentRequest:
    """
    Ajax request for page content replacement
    """

    def __init__(self, get_response):   
        self.get_response = get_response

    def __call__(self, request):
        """
        Insert is_content_request in request
        """
        if config.CORE_PAGE_CONTENT_RELOAD:
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            is_ajax = is_ajax and request.headers.get('X-Page-Content-Reload') == "Active"
            request.is_content_request = is_ajax
        else:
            request.is_content_request = False

        response = self.get_response(request)

        return response
