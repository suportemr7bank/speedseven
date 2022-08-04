"""
    API URL Configuration
"""
from django.urls import path
from django.conf import settings

from core.views import core as core_views

urlpatterns = [
    path('schema/', core_views.SpectacularAPIView.as_view(), name='schema'),
    path('redoc/', core_views.SpectacularRedocView.as_view(url_name='schema'),
         name='schema-redoc'),
]

if not settings.API_ENABLE_PRODUCTION_MODE:
    urlpatterns += [
        path('swagger/', core_views.SpectacularSwaggerView.as_view(url_name='schema'),
             name='schema-swagger-ui')
    ]
