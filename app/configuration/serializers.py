import logging

from rest_framework import serializers

from configuration.models import AdminConfiguration, Configuration, UIConfiguration

logger = logging.getLogger(__name__)


class AdminConfigurationSerializer(serializers.ModelSerializer):

    class Meta:
        model = AdminConfiguration
        fields = ['name',
                  'target',]


class ConfigurationSerializer(serializers.ModelSerializer):
    admins = AdminConfigurationSerializer(many=True)

    class Meta:
        model = Configuration
        fields = ['target_xds_api',
                  'target_xms_api',
                  'target_ldss_api',
                  'target_elrr_api',
                  'target_eccr_api',
                  'admins',]

    def to_representation(self, instance):
        """Allow restricting access to fields based on group membership"""
        d = super().to_representation(instance)
        current_user = self.context['request'].user
        user_groups = current_user.groups.all()
        manager_groups = instance.manager_group.all()
        org_admin_groups = instance.org_admin_group.all()
        # check if user is an org admin, if not remove xms and ldss
        if not org_admin_groups.intersection(user_groups).exists():
            d.pop('target_xms_api', None)
            d.pop('target_ldss_api', None)
        # check if user is in manager groups, if yes add manager flag
        if manager_groups.intersection(user_groups).exists():
            d['manager'] = True
        return d

class UIConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UIConfiguration
        fields = ['logo',
                  'portal_name',
                  'welcome_message']