from django.core.validators import RegexValidator
from django.db import models
from model_utils.models import TimeStampedModel

from external.models import Job
from portal.regex import REGEX_CHECK, REGEX_ERROR_MESSAGE


# Create your models here.
class Vacancy(TimeStampedModel):
    vacancy_key = models.CharField(primary_key=True, max_length=255,
                                   validators=[
                                       RegexValidator(
                                           regex=REGEX_CHECK,
                                           message=REGEX_ERROR_MESSAGE),
                                   ])
    vacancy_key_hash = models.CharField(max_length=255, validators=[
        RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
    ])
    job = models.ForeignKey(
        Job, on_delete=models.CASCADE,
        related_name='vacancies', blank=True, null=True)
    JobTitle = models.CharField(max_length=255, validators=[
        RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
    ])
    JobGrade = models.CharField(max_length=255,
                                blank=True, null=True, validators=[
                                    RegexValidator(
                                        regex=REGEX_CHECK,
                                        message=REGEX_ERROR_MESSAGE),
                                ])
    AgencyContactEmail = models.EmailField(max_length=255,
                                           blank=True, null=True,
                                           validators=[RegexValidator(
                                               regex=REGEX_CHECK,
                                               message=REGEX_ERROR_MESSAGE),
                                           ])
    AgencyContactPhone = models.CharField(max_length=255,
                                          null=True, blank=True, validators=[
                                              RegexValidator(
                                                  regex=REGEX_CHECK,
                                                  message=REGEX_ERROR_MESSAGE),
                                          ])
    ApplicationCloseDate = models.DateTimeField(blank=True, null=True)
    DepartmentName = models.CharField(max_length=255,
                                      blank=True, null=True, validators=[
                                          RegexValidator(
                                              regex=REGEX_CHECK,
                                              message=REGEX_ERROR_MESSAGE),
                                      ])
    AppointmentType = models.CharField(max_length=255,
                                       blank=True, null=True, validators=[
                                           RegexValidator(
                                               regex=REGEX_CHECK,
                                               message=REGEX_ERROR_MESSAGE),
                                       ])
    JobCategory = models.TextField(blank=True, null=True, validators=[
        RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
    ])
    JobCompetencies = models.TextField(blank=True, null=True, validators=[
        RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
    ])
    JobCredentials = models.TextField(blank=True, null=True, validators=[
        RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
    ])
    JobLocation = models.TextField(blank=True, null=True, validators=[
        RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
    ])
    JobPostingID = models.CharField(max_length=255, validators=[
        RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
    ])
    JobPostingSite = models.URLField(max_length=255, validators=[
        RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
    ])
    OrganizationName = models.CharField(max_length=255, validators=[
        RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
    ])
    PositionEndDate = models.DateTimeField(blank=True, null=True)
    PositionStartDate = models.DateTimeField(blank=True, null=True)
    PublicationStartDate = models.DateTimeField(blank=True, null=True)
    PromotionPotential = models.CharField(max_length=255,
                                          blank=True, null=True, validators=[
                                              RegexValidator(
                                                  regex=REGEX_CHECK,
                                                  message=REGEX_ERROR_MESSAGE),
                                          ])
    ProviderName = models.CharField(max_length=255, validators=[
        RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
    ])
    Qualifications = models.TextField(blank=True, null=True, validators=[
        RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
    ])
    Relocation = models.CharField(max_length=255, blank=True, null=True,
                                  validators=[
                                      RegexValidator(
                                          regex=REGEX_CHECK,
                                          message=REGEX_ERROR_MESSAGE),
                                  ])
    TravelRequired = models.CharField(max_length=255,
                                      blank=True, null=True, validators=[
                                          RegexValidator(
                                              regex=REGEX_CHECK,
                                              message=REGEX_ERROR_MESSAGE),
                                      ])
    UIDUnitIdentifiers = models.CharField(max_length=255, validators=[
        RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
    ])
    WorkSchedule = models.TextField(blank=True, null=True, validators=[
        RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
    ])

    def __str__(self):
        return f'{self.vacancy_key}'

    class Meta:
        verbose_name_plural = 'vacancies'
