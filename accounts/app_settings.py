from django.conf import settings


if default := getattr(settings, 'USER_PROFILE_DEFAULT_THEME'):
    USER_PROFILE_DEFAULT_THEME = default
else:
    USER_PROFILE_DEFAULT_THEME = 'dark'
