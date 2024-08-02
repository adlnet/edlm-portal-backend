from django.db import models
from external.models import Job
from model_utils.models import TimeStampedModel


# Create your models here.
class Vacancy(TimeStampedModel):
    name = models.CharField(max_length=255)
    job = models.ForeignKey(
        Job, on_delete=models.CASCADE, related_name='vacancies')

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name_plural = 'vacancies'
