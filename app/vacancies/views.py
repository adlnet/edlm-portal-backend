from django.shortcuts import render
from rest_framework import viewsets

from vacancies.models import Vacancy
from vacancies.serializers import VacancySerializer

# Create your views here.

class VacancyViewSet(viewsets.ModelViewSet):
    queryset = Vacancy.objects.all()
    serializer_class = VacancySerializer
