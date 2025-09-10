from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse
from model_utils.models import TimeStampedModel

from portal.regex import REGEX_CHECK, REGEX_ERROR_MESSAGE
from users.models import User


# Create your models here.
class Course(TimeStampedModel):
    name = models.CharField(max_length=255, blank=True, validators=[
        RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
    ])
    reference = models.CharField(max_length=255, unique=True, primary_key=True,
                                 validators=[
                                     RegexValidator(
                                         regex=REGEX_CHECK,
                                         message=REGEX_ERROR_MESSAGE),
                                 ])

    def __str__(self):
        return f'{self.name}'

    def get_absolute_url(self):
        return reverse("courses-detail", kwargs={"pk": self.pk})


class LearnerRecord(TimeStampedModel):
    name = models.CharField(max_length=255, blank=True, validators=[
        RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
    ])
    user = models.OneToOneField(User, on_delete=models.PROTECT)

    def __str__(self):
        return f'{self.name}'

    def get_absolute_url(self):
        return reverse("learners-detail", kwargs={"pk": self.pk})


class Job(TimeStampedModel):
    name = models.CharField(max_length=255, blank=True, validators=[
        RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
    ])
    reference = models.CharField(max_length=500, primary_key=True, validators=[
        RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
    ])
    job_type = models.CharField(max_length=255, blank=True, validators=[
        RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
    ])

    def __str__(self):
        return f'{self.name}'

    def get_absolute_url(self):
        return reverse("jobs-detail", kwargs={"pk": self.pk})
