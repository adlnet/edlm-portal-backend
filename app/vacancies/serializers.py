import logging

from rest_framework import serializers

from vacancies.models import Vacancy

logger = logging.getLogger(__name__)

class VacancySerializer(serializers.ModelSerializer):
    class Meta:
        model = Vacancy
        fields = ["vacancy_key", "vacancy_key_hash", "JobTitle", "JobTitle",
                  "AgencyContactEmail", "AgencyContactPhone",
                  "ApplicationCloseDate", "DepartmentName", "AppointmentType",
                  "JobCategory", "JobCompetencies", "JobCredentials", "JobLocation",
                  "JobPostingID", "JobPostingSite", "OrganizationName", "PositionEndDate",
                  "PositionStartDate", "PublicationStartDate", "PromotionPotential",
                  "ProviderName", "Qualifications", "Relocation", "TravelRequired", "UIDUnitIdentifiers",
                  "WorkSchedule"]