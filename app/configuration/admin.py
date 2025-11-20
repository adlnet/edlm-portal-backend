from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from configuration.models import AdminConfiguration, Configuration, UIConfiguration

# Register your models here.

@admin.register(UIConfiguration)
class UIConfigurationAdmin(admin.ModelAdmin):
    list_display = ('pk', 'logo', 'portal_name','welcome_message',)

@admin.register(Configuration)
class ConfigurationAdmin(admin.ModelAdmin):
    list_display = ('pk',)
    filter_horizontal = ['manager_group',
                         'org_admin_group',]

    fieldsets = (
        (
            "Base Connections",
            {
                "fields": (
                    'target_xds_api',
                    'target_elrr_api',
                    'target_eccr_api',
                )
            }
        ),
        (
            "Manager Connections",
            {
                "fields": (
                    'manager_group',
                )
            }
        ),
        (
            "Organization Admin Connections",
            {
                "fields": (
                    'target_xms_api',
                    'target_ldss_api',
                    'org_admin_group',
                )
            }
        ),
        (
            "LRS Settings",
            {
                "fields": (
                    'lrs_endpoint',
                    'lrs_username',
                    'lrs_password',
                    'lrs_platform',
                )
            }
        ),
    )


@admin.register(AdminConfiguration)
class AdminConfigurationAdmin(GuardedModelAdmin):
    list_display = ('name', 'target', )

    fieldsets = (
        (
            "General",
            {
                "fields": (
                    'name',
                    'target',
                )
            }
        ),
        (
            "Connections",
            {
                "fields": (
                    'config',
                )
            }
        ),
    )
