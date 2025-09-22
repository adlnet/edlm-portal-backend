import logging

from rest_framework import serializers

from configuration.utils.portal_utils import confusable_homoglyphs_check
from external.models import Job
from external.serializers import JobSerializer
from vacancies.models import Vacancy

logger = logging.getLogger(__name__)


class VacancySerializer(serializers.ModelSerializer):

    job = JobSerializer(required=False, allow_null=True)

    class Meta:
        model = Vacancy
        fields = ["vacancy_key", "vacancy_key_hash",
                  "JobTitle", "JobTitle",
                  "AgencyContactEmail", "AgencyContactPhone",
                  "ApplicationCloseDate", "DepartmentName",
                  "AppointmentType", "JobCategory",
                  "JobCompetencies", "JobCredentials",
                  "JobLocation", "JobPostingID",
                  "JobPostingSite", "OrganizationName",
                  "PositionEndDate", "PositionStartDate",
                  "PublicationStartDate", "PromotionPotential",
                  "ProviderName", "Qualifications", "Relocation",
                  "TravelRequired", "UIDUnitIdentifiers",
                  "WorkSchedule", "job"]

    def create(self, validated_data):

        job_data = {}
        if 'job' in validated_data:
            job_data = validated_data.pop('job')

        vacancy = Vacancy.objects.create(**validated_data)

        if job_data:
            job, c = Job.objects.get_or_create(reference=job_data["reference"],
                                               defaults=job_data)
            vacancy.job = job
            vacancy.save()

        return vacancy

    def validate(self, attrs):
        if not confusable_homoglyphs_check(attrs):
            raise serializers.ValidationError("Data contains homoglyphs and"
                                              " can be dangerous. Check logs"
                                              " for more details")
        return super().validate(attrs)
