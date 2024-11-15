import logging

from django.db.models import Prefetch
from rest_framework import permissions, viewsets
from rest_framework_guardian import filters

from configuration.models import AdminConfiguration, Configuration
from configuration.serializers import ConfigurationSerializer

logger = logging.getLogger(__name__)


# Create your views here.


class ConfigurationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Retrieve configuration information
    """
    queryset = Configuration.objects.all()
    serializer_class = ConfigurationSerializer
    filter_backends = [filters.ObjectPermissionsFilter]
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        """Restrict access to Admin Configurations"""
        return super().get_queryset().prefetch_related(
            Prefetch('admins',
                     filters.ObjectPermissionsFilter().filter_queryset(
                         self.request,
                         AdminConfiguration.objects.all(),
                         self)))
