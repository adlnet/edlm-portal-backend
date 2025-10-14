from django.contrib.postgres.fields import ArrayField
from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse
from model_utils import Choices
from model_utils.models import TimeStampedModel

from external.models import Competency, Job, Ksa
from portal.regex import REGEX_CHECK, REGEX_ERROR_MESSAGE
from users.models import User
from vacancies.models import Vacancy


# Create your models here.
class ProfileQuestion(models.Model):
    active = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(unique=True)
    question = models.TextField(unique=True, validators=[
        RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
    ])

    class Meta:
        ordering = ['order',]

    def __str__(self):
        return f'{self.order}. {self.question}'

    def get_absolute_url(self):
        return reverse("api:profile-questions-detail", kwargs={"pk": self.pk})


class ProfileAnswer(models.Model):
    question = models.ForeignKey(
        ProfileQuestion, on_delete=models.CASCADE, related_name='answers')
    order = models.PositiveSmallIntegerField()
    answer = models.TextField(validators=[
        RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
    ])

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['question', 'order',],
                name='unique_answer_order'),
            models.UniqueConstraint(
                fields=['question', 'answer'],
                name='unique_question_answer')
        ]
        ordering = ['order',]

    def __str__(self):
        return f'{self.order}. {self.answer}'


class ProfileResponse(TimeStampedModel):
    question = models.ForeignKey(
        ProfileQuestion, on_delete=models.CASCADE, related_name='responses')
    submitted_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='responses')
    selected = models.ForeignKey(
        ProfileAnswer, on_delete=models.CASCADE, related_name='responses')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['question', 'submitted_by',],
                name='unique_question_response')
        ]

    def get_absolute_url(self):
        return reverse("api:profile-responses-detail", kwargs={"pk": self.pk})


class CandidateList(TimeStampedModel):
    ranker = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='lists')
    name = models.TextField(validators=[
        RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
    ])
    role = models.ForeignKey(
        Vacancy, on_delete=models.CASCADE, related_name='recommended',
        null=True, blank=True)
    competency = models.ForeignKey(
        Job, on_delete=models.CASCADE, related_name='recommended',
        null=True, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(role__isnull=True) ^ models.Q(
                    competency__isnull=True), name="role_or_competency")
        ]

    def __str__(self):
        return f'{self.name} - {self.role if self.competency is None
                                else self.competency} ({self.ranker})'

    def get_absolute_url(self):
        return reverse("api:candidate-lists-detail", kwargs={"pk": self.pk})


class CandidateRanking(TimeStampedModel):
    candidate_list = models.ForeignKey(
        CandidateList, on_delete=models.CASCADE, related_name='rankings')
    candidate = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='rankings')
    rank = models.PositiveSmallIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['candidate_list', 'rank',],
                name='unique_list_ranks'),
            models.UniqueConstraint(
                fields=['candidate_list', 'candidate'],
                name='unique_candidates_in_list')
        ]
        ordering = ['rank',]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.candidate_list.save(update_fields=['modified',])

    def __str__(self):
        return f'{self.rank}. {self.candidate} in {self.candidate_list}'

    def get_absolute_url(self):
        return reverse("api:candidate-rankings-detail", kwargs={"pk": self.pk})


class TrainingPlan(TimeStampedModel):
    trainee = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='training_plans_for_me')
    planner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='training_plans_by_me')
    role = models.ForeignKey(
        Job, on_delete=models.CASCADE, related_name='training_plans',
        null=True, blank=True)

    def get_absolute_url(self):
        return reverse("api:training-plans-detail", kwargs={"pk": self.pk})


class LearningPlan(TimeStampedModel):
    """Model to store learning plans detail"""
    TIMEFRAME_CHOICES = Choices('Short-term (1-2 years)',
                                'Long-term (3-4 years)')
    learner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='learning_plans')
    name = models.TextField(validators=[
        RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
    ])
    timeframe = models.CharField(max_length=50, choices=TIMEFRAME_CHOICES)

    def __str__(self):
        return f'{self.name} - {self.learner} ({self.timeframe})'

    def get_absolute_url(self):
        return reverse("api:learning-plans-detail", kwargs={"pk": self.pk})


class LearningPlanCompetency(TimeStampedModel):
    """Model to store competencies for a learning plan"""
    PRIORITY_CHOICES = Choices('Highest', 'High', 'Medium', 'Low', 'Lowest')
    learning_plan = models.ForeignKey(
        LearningPlan, on_delete=models.CASCADE, related_name='competencies')
    eccr_competency = models.ForeignKey(
        Competency, on_delete=models.CASCADE,
        related_name='learning_plans_competencies')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.learning_plan.save(update_fields=['modified',])

    # Return the name of the competency
    @property
    def plan_competency_name(self):
        return self.eccr_competency.name

    def __str__(self):
        return (f'{self.plan_competency_name} - '
                f'{self.learning_plan} ({self.priority})')

    def get_absolute_url(self):
        return reverse("api:learning-plan-competencies-detail",
                       kwargs={"pk": self.pk})


class LearningPlanGoal(TimeStampedModel):
    """Model to store goals for a learning plan"""
    plan_competency = models.ForeignKey(
        LearningPlanCompetency, on_delete=models.CASCADE, related_name='goals')
    goal_name = models.TextField(validators=[
        RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
    ])
    timeline = models.CharField(max_length=20, validators=[
        RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
    ])

    # store a list of selected choices
    resources_support = ArrayField(
        models.CharField(
            max_length=500,
            validators=[RegexValidator(
                regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE)],
        ),
        default=list,
        blank=True,
    )

    obstacles = ArrayField(
        models.CharField(
            max_length=500,
            validators=[RegexValidator(
                regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE)],
        ),
        default=list,
        blank=True,
    )

    resources_support_other = models.TextField(blank=True, validators=[
        RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
    ])
    obstacles_other = models.TextField(blank=True, validators=[
        RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
    ])

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.plan_competency.learning_plan.save(update_fields=['modified'])

    def __str__(self):
        return f'{self.goal_name} - {self.plan_competency} ({self.timeline})'

    def get_absolute_url(self):
        return reverse("api:learning-plan-goals-detail",
                       kwargs={"pk": self.pk})


class LearningPlanGoalKsa(TimeStampedModel):
    """Model to store KSAs for a learning plan goal"""
    plan_goal = models.ForeignKey(
        LearningPlanGoal, on_delete=models.CASCADE, related_name='ksas')
    eccr_ksa = models.ForeignKey(
        Ksa, on_delete=models.CASCADE, related_name='learning_plans_ksas')
    current_proficiency = models.CharField(max_length=20, validators=[
        RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
    ])
    target_proficiency = models.CharField(max_length=20, validators=[
        RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
    ])

    # Return the name of the KSA
    @property
    def ksa_name(self):
        return self.eccr_ksa.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        (self.plan_goal.plan_competency.learning_plan
         .save(update_fields=['modified']))

    def __str__(self):
        return (f'{self.ksa_name} - {self.plan_goal}'
                f'({self.current_proficiency} - {self.target_proficiency})')

    def get_absolute_url(self):
        return reverse("api:learning-plan-goal-ksas-detail",
                       kwargs={"pk": self.pk})
