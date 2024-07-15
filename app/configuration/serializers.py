import logging

from configuration.models import Configuration
from rest_framework import serializers

logger = logging.getLogger(__name__)


class ConfigurationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Configuration
        fields = ['target_xds_api', 'target_elrr_api', 'target_eccr_api',]
