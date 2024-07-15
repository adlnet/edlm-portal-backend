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
    """
    Retrieve all active Profile Questions
    """
    queryset = ProfileQuestion.objects.filter(active=True)
    serializer_class = ProfileQuestionSerializer
    filter_backends = [filter.SearchFilter, filter.OrderingFilter]
    search_fields = ['order', 'question',]
    ordering_fields = ['order',]
    ordering = ['order',]


class ProfileResponseViewSet(viewsets.ModelViewSet):
    """
    Retrieve all responses of current user for active Profile Questions
    """
    queryset = ProfileResponse.objects.filter(question__active=True)
    serializer_class = ProfileResponseSerializer
    filter_backends = [DjangoFilterBackend, filters.ObjectPermissionsFilter,]

    def initial(self, request, *args, **kwargs):
        """
        pop submitted_by value to use current user as default
        """
        if hasattr(request, 'data') and 'submitted_by' in request.data:
            request.data.pop('submitted_by')
        request = super().initial(request, *args, **kwargs)
        return request

    def get_queryset(self):
        """
        This view should return a list of all the responses
        for the currently authenticated user.
        """
        user = self.request.user
        return self.queryset.filter(submitted_by=user)
