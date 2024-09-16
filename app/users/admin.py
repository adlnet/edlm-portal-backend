from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import Organization, User

# Register your models here.


@admin.register(User)
class UserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + \
        (("Organizations", {"fields": ("organization", )},),)


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent',)

    fieldsets = (
        (
            "General",
            {
                # on the same line
                "fields": (
                    "name",
                )
            },
        ),
        (
            "Connections",
            {
                "fields": (
                    "parent",
                )
            }
        ),
    )
