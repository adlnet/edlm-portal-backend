from django.contrib import admin, messages
from django.utils.translation import ngettext

from api.models import ProfileAnswer, ProfileQuestion, ProfileResponse

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
    actions = ["remove_responses",
               "activate_questions", "deactivate_questions",]

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

    @admin.action(description="Remove related Profile Responses",
                  permissions=["delete",])
    def remove_responses(self, request, queryset):
        removed = ProfileResponse.objects.filter(
            question__in=queryset).delete()[0]

        self.message_user(
            request,
            ngettext(
                "%d Profile Response was successfully deleted.",
                "%d Profile Responses were successfully deleted.",
                removed,
            )
            % removed,
            messages.SUCCESS,
        )

    @admin.action(description="Activate selected Profile Questions",
                  permissions=["change",])
    def activate_questions(self, request, queryset):
        updated = queryset.update(active=True)

        self.message_user(
            request,
            ngettext(
                "%d Profile Question was successfully activated.",
                "%d Profile Questions were successfully activated.",
                updated,
            )
            % updated,
            messages.SUCCESS,
        )

    @admin.action(description="Deactivate selected Profile Questions",
                  permissions=["change",])
    def deactivate_questions(self, request, queryset):
        updated = queryset.update(active=False)

        self.message_user(
            request,
            ngettext(
                "%d Profile Question was successfully deactivated.",
                "%d Profile Questions were successfully deactivated.",
                updated,
            )
            % updated,
            messages.SUCCESS,
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
