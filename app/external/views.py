import logging

from rest_framework import filters as filter
from rest_framework import viewsets

from external.models import Course, Job, LearnerRecord
from external.serializers import (CourseSerializer, JobSerializer,
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
    # ordering_fields = ['order',]
    # ordering = ['order',]


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
