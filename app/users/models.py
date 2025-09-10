from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from portal.regex import REGEX_CHECK, REGEX_ERROR_MESSAGE

# Create your models here.


class Organization(models.Model):
    name = models.CharField(max_length=255, validators=[
        RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
    ])
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f'{self.name} - {self.parent}' if self.parent else self.name


class User(AbstractUser):
    organization = models.ForeignKey(
        Organization, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='members')
