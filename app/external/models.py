from django.db import models
from model_utils.models import TimeStampedModel

from users.models import User


# Create your models here.
class Course(TimeStampedModel):
    name = models.CharField(max_length=255)
    reference = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return f'{self.name}'


class LearnerRecord(TimeStampedModel):
    name = models.CharField(max_length=255)
    user = models.OneToOneField(User, on_delete=models.PROTECT)

    def __str__(self):
        return f'{self.name}'


class Job(TimeStampedModel):
    name = models.CharField(max_length=255)
    reference = models.CharField(max_length=255, unique=True)
    job_type = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.name}'
