import logging

from django.db.models import Prefetch
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters as filter
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework_guardian import filters

from api.models import (CandidateList, CandidateRanking, ProfileQuestion,
                        ProfileResponse, TrainingPlan)
from api.serializers import (CandidateListSerializer,
                             CandidateRankingSerializer,
                             ProfileQuestionSerializer,
                             ProfileResponseSerializer, TrainingPlanSerializer)

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

@method_decorator(csrf_exempt, name="dispatch")
class CandidateListViewSet(viewsets.ModelViewSet):
    """
    Retrieve Candidate List
    """
    queryset = CandidateList.objects.all().select_related(
        "ranker", "role", "competency"
    ).prefetch_related(
        Prefetch(
            "rankings",
            queryset=CandidateRanking.objects.order_by("rank")),
        "rankings__candidate").order_by("-modified")
    serializer_class = CandidateListSerializer
    filter_backends = [filters.ObjectPermissionsFilter,]

    def initial(self, request, *args, **kwargs):
        """
        pop submitted_by value to use current user as default
        """
        if hasattr(request, 'data') and 'ranker' in request.data:
            request.data.pop('ranker')
        request = super().initial(request, *args, **kwargs)
        return request


class CandidateRankingViewSet(viewsets.ModelViewSet):
    """
    Retrieve Candidate Rankings
    """
    queryset = CandidateRanking.objects.all()
    serializer_class = CandidateRankingSerializer
    filter_backends = [DjangoFilterBackend, filters.ObjectPermissionsFilter,]

    def create(self, request, *args, **kwargs):
        candidate_list_pk = request.data.get('candidate_list')
        cl = CandidateList.objects.get(pk=candidate_list_pk)
        if not request.user.has_perm('api.change_candidatelist', cl):
            return Response({'detail': 'You do not have permission'
                             ' to perform this action'},
                            status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)

    def get_queryset(self):
        """
        This view should return a list of all the responses
        for the currently authenticated user.
        """
        user = self.request.user
        return self.queryset.filter(
            candidate_list__ranker=user
        ).select_related("candidate", "candidate_list")


class TrainingPlanListViewSet(viewsets.ModelViewSet):
    """
    Retrieve Training Plans
    """
    queryset = TrainingPlan.objects.all().select_related(
        "planner", "role", "trainee")
    serializer_class = TrainingPlanSerializer
    filter_backends = [filters.ObjectPermissionsFilter,]

    def initial(self, request, *args, **kwargs):
        """
        pop submitted_by value to use current user as default
        """
        if hasattr(request, 'data') and 'planner' in request.data:
            request.data.pop('planner')
        request = super().initial(request, *args, **kwargs)
        return request
