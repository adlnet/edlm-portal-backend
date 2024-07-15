from django.db import models
from django.urls import reverse
from model_utils.models import TimeStampedModel

from users.models import User


# Create your models here.
class ProfileQuestion(models.Model):
    active = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField()
    question = models.TextField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['active', 'order',],
                name='unique_active_question_order'),
            models.UniqueConstraint(
                fields=['active', 'order', 'question'],
                name='fully_unique_question'),
        ]

    def __str__(self):
        return f'{self.order}. {self.question}'

    def get_absolute_url(self):
        return reverse("profile-questions", kwargs={"pk": self.pk})


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
                fields=['question', 'order', 'answer'],
                name='fully_unique_answer')
        ]

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
        return reverse("profile-responses", kwargs={"pk": self.pk})
