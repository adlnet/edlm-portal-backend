import logging

from configuration.models import Configuration
from configuration.serializers import ConfigurationSerializer
from rest_framework import viewsets

logger = logging.getLogger(__name__)


# Create your views here.


class ConfigurationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Configuration.objects.all()
    serializer_class = ConfigurationSerializer
