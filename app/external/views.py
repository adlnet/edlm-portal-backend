import logging

from rest_framework import filters as filter
from rest_framework import viewsets

from external.models import Competency, Course, Job, Ksa, LearnerRecord
from external.serializers import (CompetencySerializer, CourseSerializer,
                                  JobSerializer,  KsaSerializer,
                                  LearnerRecordSerializer)

logger = logging.getLogger(__name__)


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Retrieve all Course objects
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    filter_backends = [filter.SearchFilter,]
    search_fields = ['reference',]


class JobViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Retrieve all Job objects
    """
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    filter_backends = [filter.SearchFilter,]
    search_fields = ['reference', 'job_type',]


class LearnerRecordViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Retrieve all LearnerRecord objects
    """
    queryset = LearnerRecord.objects.all()
    serializer_class = LearnerRecordSerializer
    filter_backends = [filter.SearchFilter,]
    search_fields = ['user__email',]


class CompetencyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Retrieve all Competency objects
    """
    queryset = Competency.objects.all()
    serializer_class = CompetencySerializer
    filter_backends = [filter.SearchFilter,]
    search_fields = ['reference',]


class KsaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Retrieve all Ksa objects
    """
    queryset = Ksa.objects.all()
    serializer_class = KsaSerializer
    filter_backends = [filter.SearchFilter,]
    search_fields = ['reference',]
