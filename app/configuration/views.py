import logging

from django.db.models import Prefetch
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework_guardian import filters

from configuration.models import (AdminConfiguration,
                                  Configuration,
                                  UIConfiguration)
from configuration.serializers import (ConfigurationSerializer,
                                       UIConfigurationSerializer)

logger = logging.getLogger(__name__)

# Create your views here.


class ConfigurationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Retrieve configuration information
    """
    queryset = Configuration.objects.all()
    serializer_class = ConfigurationSerializer
    filter_backends = [filters.ObjectPermissionsFilter]

    def get_queryset(self):
        """Restrict access to Admin Configurations"""
        return super().get_queryset().prefetch_related(
            Prefetch('admins',
                     filters.ObjectPermissionsFilter().filter_queryset(
                         self.request,
                         AdminConfiguration.objects.all(),
                         self)))


class UIConfigurationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Retrieve UI configuration information
    """
    queryset = UIConfiguration.objects.all()
    serializer_class = UIConfigurationSerializer

    def list(self, request, *args, **kwargs):
        config = self.get_queryset().first()
        serializer = self.get_serializer(config)
        return Response(serializer.data)
