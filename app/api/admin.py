from django.contrib import admin

from api.models import ProfileAnswer, ProfileQuestion

# Register your models here.


class ProfileAnswerInline(admin.TabularInline):
    can_delete = False
    model = ProfileAnswer
    fields = ('order', 'answer',)
    extra = 3


@admin.register(ProfileQuestion)
class ProfileQuestionAdmin(admin.ModelAdmin):
    list_display = ('active', 'order', 'question')

    inlines = [ProfileAnswerInline]

    # fields to display in the admin site
    fieldsets = (
        (
            "General",
            {
                # on the same line
                "fields": (
                    "question",
                )
            },
        ),
        (
            "Status",
            {
                "fields": (
                    "active",
                    "order",
                )
            }
        ),
    )


@admin.register(ProfileAnswer)
class ProfileAnswerAdmin(admin.ModelAdmin):
    list_display = ('order', 'answer', 'question')

    fieldsets = (
        (
            "General",
            {
                # on the same line
                "fields": (
                    "answer",
                )
            },
        ),
        (
            "Connections",
            {
                "fields": (
                    "question",
                )
            }
        ),
        (
            "Status",
            {
                "fields": (
                    "order",
                )
            }
        ),
    )
