"""
Django channels routing
"""

from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path('ws/send-batch-mail/', consumers.EmailBatchConsumer.as_asgi()),
]
