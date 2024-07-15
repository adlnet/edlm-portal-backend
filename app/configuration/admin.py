from configuration.models import Configuration
from django.contrib import admin

# Register your models here.


@admin.register(Configuration)
class ConfigurationAdmin(admin.ModelAdmin):
    list_display = ('target_xds_api', 'target_elrr_api', 'target_eccr_api')

    fieldsets = (
        (
            "Connections",
            {
                "fields": (
                    'target_xds_api',
                    'target_elrr_api',
                    'target_eccr_api',
                )
            }
        ),
    )
