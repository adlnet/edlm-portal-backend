import logging

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters as filter
from rest_framework import viewsets
from rest_framework_guardian import filters

from api.models import ProfileQuestion, ProfileResponse
from api.serializers import (ProfileQuestionSerializer,
                             ProfileResponseSerializer)

logger = logging.getLogger(__name__)


# Create your views here.


class ProfileQuestionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProfileQuestion.objects.filter(active=True)
    serializer_class = ProfileQuestionSerializer
    filter_backends = [filter.SearchFilter, filter.OrderingFilter]
    search_fields = ['order',]
    ordering_fields = ['order',]


class ProfileResponseViewSet(viewsets.ModelViewSet):
    queryset = ProfileResponse.objects.all()
    serializer_class = ProfileResponseSerializer
    filter_backends = [DjangoFilterBackend, filters.ObjectPermissionsFilter,
                       filter.SearchFilter,]
    filterset_fields = ['submitted_by', ]
    search_fields = ['question']
