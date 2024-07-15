from django.db import models
from django.forms import ValidationError
from django.urls import reverse

# Create your models here.


class Configuration(models.Model):
    target_xds_api = models.CharField(
        max_length=200,
        help_text='Enter the XDS api endpoint to query',
        default='http://localhost:8080/')

    target_elrr_api = models.CharField(
        max_length=200,
        help_text='Enter the ELRR api endpoint to query',
        default='http://localhost:9200/')

    target_eccr_api = models.CharField(
        max_length=200,
        help_text='Enter the ECCR api endpoint to query',
        default='http://localhost:9200/')

    def save(self, *args, **kwargs):
        if not self.pk and Configuration.objects.exists():
            # if you'll not check for self.pk
            # then error will also be raised in the update of exists model
            raise ValidationError(
                'There is can be only one Configuration instance')
        return super(Configuration, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("config", kwargs={"pk": self.pk})
