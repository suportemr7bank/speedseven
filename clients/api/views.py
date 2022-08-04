"""
Client api views
"""

from rest_framework import generics

from .. import models
from . import serializers


class ClientCreateView(generics.CreateAPIView):
    """
    Client create view
    """
    serializer_class = serializers.ClientSerializer
    # pylint: disable=no-member
    queryset = models.Client.objects.all()


class ClientRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    """
    Client update and retrieve view
    """
    serializer_class = serializers.ClientSerializer
    # pylint: disable=no-member
    queryset = models.Client.objects.all()
