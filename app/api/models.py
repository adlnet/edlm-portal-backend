from django.db import models
from django.urls import reverse
from model_utils.models import TimeStampedModel
from vacancies.models import Vacancy

from users.models import User


# Create your models here.
class ProfileQuestion(models.Model):
    active = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(unique=True)
    question = models.TextField(unique=True)

    class Meta:
        ordering = ['order',]

    def __str__(self):
        return f'{self.order}. {self.question}'

    def get_absolute_url(self):
        return reverse("profile-questions-detail", kwargs={"pk": self.pk})


class ProfileAnswer(models.Model):
    question = models.ForeignKey(
        ProfileQuestion, on_delete=models.CASCADE, related_name='answers')
    order = models.PositiveSmallIntegerField()
    answer = models.TextField()

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
        return reverse("profile-responses-detail", kwargs={"pk": self.pk})


class CandidateList(TimeStampedModel):
    ranker = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='lists')
    name = models.TextField()
    role = models.ForeignKey(
        Vacancy, on_delete=models.CASCADE, related_name='recommended')

    def __str__(self):
        return f'{self.name} - {self.role} ({self.ranker})'


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

    def __str__(self):
        return f'{self.rank}. {self.candidate} in {self.candidate_list}'
