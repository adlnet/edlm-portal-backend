import logging

from django.conf import settings
from django.db.models import Prefetch
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters as filter
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_guardian import filters

from api.models import (CandidateList, CandidateRanking, ProfileQuestion,
                        ProfileResponse, TrainingPlan)
from api.serializers import (CandidateListSerializer,
                             CandidateRankingSerializer,
                             ProfileQuestionSerializer,
                             ProfileResponseSerializer, TrainingPlanSerializer)
from api.utils.xapi_utils import (COURSE_PROGRESS_VERBS,
                                  filter_courses_by_exclusion,
                                  get_lrs_statements,
                                  jwt_account_name,
                                  process_course_statements,
                                  remove_duplicates)
from configuration.models import Configuration
from external.models import LearnerRecord

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
            request.data._mutable = True
            request.data.pop('submitted_by')
            request.data._mutable = False
        request = super().initial(request, *args, **kwargs)
        return request

    def get_queryset(self):
        """
        This view should return a list of all the responses
        for the currently authenticated user.
        """
        user = self.request.user
        return self.queryset.filter(submitted_by=user)


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
            request.data._mutable = True
            request.data.pop('ranker')
            request.data._mutable = False
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
            request.data._mutable = True
            request.data.pop('planner')
            request.data._mutable = False
        request = super().initial(request, *args, **kwargs)
        return request


class GetCourseProgressView(APIView):
    """Handles xAPI Course Progress Data Requests"""

    queryset = LearnerRecord.objects.all()

    def get(self, request):
        """Get course progress data"""

        config = Configuration.objects.first()
        if not config:
            return Response({'message': 'No configuration found.'},
                            status.HTTP_500_INTERNAL_SERVER_ERROR)

        lrs_endpoint = config.lrs_endpoint
        lrs_username = config.lrs_username
        lrs_password = config.lrs_password
        lrs_platform = config.lrs_platform

        if not (lrs_endpoint and lrs_username and lrs_password):
            return Response({'message': 'LRS credentials not configured.'},
                            status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Get User identifier (email)
        user_identifier = None
        if settings.XAPI_USE_JWT:
            account_name = jwt_account_name(
                request,
                settings.XAPI_ACTOR_ACCOUNT_NAME_JWT_FIELDS
            )
            if account_name is None:
                # Return a 400 if none matched
                return Response(
                    {"message": "No valid JWT field found."},
                    status.HTTP_400_BAD_REQUEST
                )
            user_identifier = account_name
        else:
            if request.user.is_authenticated:
                user_identifier = request.user.email  # Safe to access
            else:
                return Response({'message': 'Could not get xAPI user'
                                ' identifier information.'},
                                status.HTTP_400_BAD_REQUEST)

        try:
            # Get completed statements
            completed_statements = get_lrs_statements(
                lrs_endpoint,
                lrs_username,
                lrs_password,
                user_identifier,
                COURSE_PROGRESS_VERBS['completed'],
                lrs_platform
            )
            # Get enrolled statements
            enrolled_statements = get_lrs_statements(
                lrs_endpoint,
                lrs_username,
                lrs_password,
                user_identifier,
                COURSE_PROGRESS_VERBS['enrolled'],
                lrs_platform
            )
            # Get in-progress statements
            in_progress_statements = get_lrs_statements(
                lrs_endpoint,
                lrs_username,
                lrs_password,
                user_identifier,
                COURSE_PROGRESS_VERBS['in-progress'],
                lrs_platform
            )

            # Process statements
            completed_courses = process_course_statements(
                completed_statements, "completed")
            enrolled_courses = process_course_statements(
                enrolled_statements, "enrolled")
            in_progress_courses = process_course_statements(
                in_progress_statements, "in-progress")

            # Remove any duplicates
            completed_courses = remove_duplicates(completed_courses)
            enrolled_courses = remove_duplicates(enrolled_courses)
            in_progress_courses = remove_duplicates(in_progress_courses)

            # Keep only in-progress courses that aren't already completed
            in_progress_courses = filter_courses_by_exclusion(
                in_progress_courses, completed_courses)

            resp_data = {
                'completed_courses': completed_courses,
                'enrolled_courses': enrolled_courses,
                'in_progress_courses': in_progress_courses
            }

            return Response(resp_data, status.HTTP_200_OK)

        except ConnectionError:
            return Response({'message': 'Could not connect to LRS'},
                            status.HTTP_502_BAD_GATEWAY)
        except Exception:
            return Response({'message': 'An error occurred while'
                            ' fetching user course progress'},
                            status.HTTP_500_INTERNAL_SERVER_ERROR)
