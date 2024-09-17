from django.db import models
from model_utils.models import TimeStampedModel

from external.models import Job


# Create your models here.
class Vacancy(TimeStampedModel):
    vacancy_key = models.CharField(primary_key=True, max_length=255)
    vacancy_key_hash = models.CharField(max_length=255)
    job = models.ForeignKey(
        Job, on_delete=models.CASCADE, related_name='vacancies', blank=True, null=True)
    JobTitle = models.CharField(max_length=255)
    JobGrade = models.CharField(max_length=255, blank=True, null=True)
    AgencyContactEmail = models.EmailField(max_length=255, blank=True, null=True)
    AgencyContactPhone = models.CharField(max_length=255, null=True, blank=True)
    ApplicationCloseDate = models.DateTimeField(blank=True, null=True)
    DepartmentName = models.CharField(max_length=255, blank=True, null=True)
    AppointmentType = models.CharField(max_length=255, blank=True, null=True)
    JobCategory = models.TextField(blank=True, null=True)
    JobCompetencies = models.TextField(blank=True, null=True)
    JobCredentials = models.TextField(blank=True, null=True)
    JobLocation = models.TextField(blank=True, null=True)
    JobPostingID = models.CharField(max_length=255)
    JobPostingSite = models.URLField(max_length=255)
    OrganizationName = models.CharField(max_length=255)
    PositionEndDate = models.DateTimeField(blank=True, null=True)
    PositionStartDate = models.DateTimeField(blank=True, null=True)
    PublicationStartDate = models.DateTimeField(blank=True, null=True)
    PromotionPotential = models.CharField(max_length=255, blank=True, null=True)
    ProviderName = models.CharField(max_length=255)
    Qualifications = models.TextField(blank=True, null=True)
    Relocation = models.CharField(max_length=255, blank=True, null=True)
    TravelRequired = models.CharField(max_length=255, blank=True, null=True)
    UIDUnitIdentifiers = models.CharField(max_length=255)
    WorkSchedule = models.TextField(blank=True, null=True)


    def __str__(self):
        return f'{self.vacancy_key}'

    class Meta:
        verbose_name_plural = 'vacancies'
