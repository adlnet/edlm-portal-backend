from rest_framework import permissions, viewsets

from vacancies.models import Vacancy
from vacancies.serializers import VacancySerializer

# Create your views here.


class VacancyViewSet(viewsets.ModelViewSet):
    queryset = Vacancy.objects.all().filter(job__pk__isnull=False)
    serializer_class = VacancySerializer
    permission_classes = [permissions.AllowAny]
