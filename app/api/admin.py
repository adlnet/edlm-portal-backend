from django.contrib import admin, messages
from django.utils.translation import ngettext
from guardian.admin import GuardedModelAdmin

from api.models import (CandidateList, CandidateRanking, ProfileAnswer,
                        ProfileQuestion, ProfileResponse, TrainingPlan,
                        LearningPlan, LearningPlanCompetency, LearningPlanGoal,
                        LearningPlanGoalCourse, LearningPlanGoalKsa, 
                        Application, ApplicationCourse, 
                        ApplicationComment, ApplicationExperience)


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


class CandidateRankingInline(admin.TabularInline):
    can_delete = False
    model = CandidateRanking
    fields = ('candidate', 'rank',)
    extra = 3


@admin.register(CandidateList)
class CandidateListAdmin(GuardedModelAdmin):
    list_display = ('name', 'role', 'competency', 'ranker')
    list_filter = ("ranker", "role", 'competency',)
    readonly_fields = ('modified', 'created',)
    date_hierarchy = 'modified'

    inlines = [CandidateRankingInline]

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
                    "role",
                    "competency",
                    "ranker",
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


@admin.register(CandidateRanking)
class CandidateRankingAdmin(GuardedModelAdmin):
    list_display = ('candidate', 'candidate_list', 'rank',)
    list_filter = ("candidate", "candidate_list",)
    ordering = ("candidate_list", "rank",)
    readonly_fields = ('modified', 'created',)
    date_hierarchy = 'modified'

    fieldsets = (
        (
            "General",
            {
                # on the same line
                "fields": (
                    "rank",
                )
            },
        ),
        (
            "Connections",
            {
                "fields": (
                    "candidate_list",
                    "candidate",
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


@admin.register(TrainingPlan)
class TrainingPlanAdmin(GuardedModelAdmin):
    list_display = ('trainee', 'planner', 'role',)
    list_filter = ("trainee", "planner", "role",)
    ordering = ("trainee", "planner", "role",)
    readonly_fields = ('modified', 'created',)
    date_hierarchy = 'modified'

    fieldsets = (
        (
            "Connections",
            {
                "fields": (
                    "trainee",
                    "planner",
                    "role",
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


@admin.register(LearningPlan)
class LearningPlanAdmin(GuardedModelAdmin):
    list_display = ('name', 'learner', 'timeframe', 'modified')
    list_filter = ('learner', 'timeframe', 'modified')


@admin.register(LearningPlanCompetency)
class LearningPlanCompetencyAdmin(GuardedModelAdmin):
    list_display = ('learning_plan', 'plan_competency_name',
                    'priority', 'modified')
    list_filter = ('learning_plan__learner', 'priority', 'modified')


@admin.register(LearningPlanGoal)
class LearningPlanGoalAdmin(GuardedModelAdmin):
    list_display = ('goal_name', 'plan_competency', 'timeline', 'modified')
    list_filter = ('plan_competency__learning_plan__learner',
                   'timeline', 'modified')


@admin.register(LearningPlanGoalKsa)
class LearningPlanGoalKsaAdmin(GuardedModelAdmin):
    list_display = ('ksa_name', 'plan_goal', 'current_proficiency',
                    'target_proficiency', 'modified')
    list_filter = ('plan_goal__plan_competency__learning_plan__learner',
                   'current_proficiency', 'target_proficiency', 'modified')


@admin.register(LearningPlanGoalCourse)
class LearningPlanGoalCourseAdmin(GuardedModelAdmin):
    list_display = ('course_name', 'plan_goal', 'modified')
    list_filter = ('plan_goal__plan_competency__learning_plan__learner',
                   'modified')


@admin.register(Application)
class ApplicationAdmin(GuardedModelAdmin):
    list_display = ('applicant', 'application_type', 'position', 'status', 'final_submission')
    list_filter = ('application_type', 'position', 'status', 'final_submission')


@admin.register(ApplicationCourse)
class ApplicationCourseAdmin(GuardedModelAdmin):
    list_display = ('application', 'completion_date',)
    list_filter = ('application__applicant',)


@admin.register(ApplicationExperience)
class ApplicationExperienceAdmin(GuardedModelAdmin):
    list_display = ('application', 'position_name', 'start_date', 'end_date')
    list_filter = ('application__applicant',)


@admin.register(ApplicationComment)
class ApplicationCommentAdmin(GuardedModelAdmin):
    list_display = ('application', 'reviewer')
    list_filter = ('application__applicant',)
