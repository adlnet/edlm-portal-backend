from django.contrib import admin

from external.models import Course, Job, LearnerRecord

# Register your models here.


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('name', 'job_type', 'reference')
    list_filter = ("job_type",)
    readonly_fields = ('modified', 'created',)
    date_hierarchy = 'modified'
    # ordering = ("question", "order",)

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
            "Connection",
            {
                "fields": (
                    "job_type",
                    "reference",
                )
            }
        ),
        (
            "Meta",
            {
                "classes": ["collapse"],
                "fields": (
                    "modified",
                    "created",
                )
            }
        ),
    )


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'reference',)
    # list_filter = ("candidate", "candidate_list",)
    # ordering = ("candidate_list", "rank",)
    readonly_fields = ('modified', 'created',)
    date_hierarchy = 'modified'

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
                    "reference",
                )
            }
        ),
        (
            "Meta",
            {
                "classes": ["collapse"],
                "fields": (
                    "modified",
                    "created",
                )
            }
        ),
    )


@admin.register(LearnerRecord)
class LearnerRecordAdmin(admin.ModelAdmin):
    list_display = ('name', 'user',)
    # list_filter = ("candidate", "candidate_list",)
    # ordering = ("candidate_list", "rank",)
    readonly_fields = ('modified', 'created',)
    date_hierarchy = 'modified'

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
                    "user",
                )
            }
        ),
        (
            "Meta",
            {
                "classes": ["collapse"],
                "fields": (
                    "modified",
                    "created",
                )
            }
        ),
    )
