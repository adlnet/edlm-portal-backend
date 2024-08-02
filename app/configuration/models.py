from django.contrib.auth.models import Group
from django.db import models
from django.forms import ValidationError
from django.urls import reverse

# Create your models here.


class Configuration(models.Model):
    target_xds_api = models.CharField(
        max_length=200,
        help_text='Enter the XDS api endpoint to query',
        default='http://localhost:8100/')

    target_xms_api = models.CharField(
        max_length=200,
        help_text='Enter the XMS api endpoint to query',
        default='http://localhost:8000/')

    target_ldss_api = models.CharField(
        max_length=200,
        help_text='Enter the LDSS admin endpoint',
        default='http://localhost:8010/')

    target_elrr_api = models.CharField(
        max_length=200,
        help_text='Enter the ELRR api endpoint to query',
        default='http://localhost:9200/')

    target_eccr_api = models.CharField(
        max_length=200,
        help_text='Enter the ECCR api endpoint to query',
        default='http://localhost:9200/')

    manager_group = models.ManyToManyField(
        Group,
        related_name='manager_config',
        help_text='Groups that should have Talent Manger permissions')

    org_admin_group = models.ManyToManyField(
        Group,
        related_name='org_admin_config',
        help_text='Groups that should have Org Admin permissions')

    def save(self, *args, **kwargs):
        if not self.pk and Configuration.objects.exists():
            # if you'll not check for self.pk
            # then error will also be raised in the update of exists model
            raise ValidationError(
                'There is can be only one Configuration instance')
        return super(Configuration, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("config-detail", kwargs={"pk": self.pk})


class AdminConfiguration(models.Model):
    name = models.CharField(
        max_length=200,
        help_text='Enter a human readable name for this Admin',
        default='XIS Admin', unique=True)

    target = models.CharField(
        max_length=200,
        help_text='Enter the Admin endpoint',
        default='http://localhost:8000/admin/')

    config = models.ForeignKey(
        Configuration, on_delete=models.CASCADE, related_name='admins')
