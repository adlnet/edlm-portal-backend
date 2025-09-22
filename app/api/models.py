from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse
from model_utils.models import TimeStampedModel

from external.models import Job
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
