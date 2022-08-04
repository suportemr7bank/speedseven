"""
Page content request middleware
"""

from accounts import app_settings

class ThemeMiddleware:
    """
    User profile theme in request
    """

    def __init__(self, get_response):   
        self.get_response = get_response

    def __call__(self, request):
        """
        Insert color theme in request
        """

        if profile := getattr(request.user, 'userprofile', None):
            theme = profile.theme
        else:
            theme = app_settings.USER_PROFILE_DEFAULT_THEME

        request.theme = theme


        response = self.get_response(request)

        return response
