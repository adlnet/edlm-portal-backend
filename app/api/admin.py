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
    list_display = ('question', 'order', 'active')
    list_filter = ("active",)
    ordering = ("order",)

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
    list_display = ('answer', 'order', 'question')
    list_filter = ("question",)
    ordering = ("question", "order",)

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
