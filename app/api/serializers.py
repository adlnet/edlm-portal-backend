import logging

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from rest_framework_guardian.serializers import \
    ObjectPermissionsAssignmentMixin

from api.models import (CandidateList, CandidateRanking, ProfileAnswer,
                        ProfileQuestion, ProfileResponse, TrainingPlan)
from configuration.utils.portal_utils import confusable_homoglyphs_check
from external.models import Job
from users.models import User
from vacancies.models import Vacancy

logger = logging.getLogger(__name__)
HOMOGLYPH_ERROR = "Data contains homoglyphs and can be dangerous. Check" + \
    " logs for more details"


class ProfileAnswerSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProfileAnswer
        fields = ['order', 'answer', 'id']

    def validate(self, attrs):
        if not confusable_homoglyphs_check(attrs):

            raise serializers.ValidationError(HOMOGLYPH_ERROR)
        return super().validate(attrs)


class ProfileQuestionSerializer(serializers.ModelSerializer):
    answers = ProfileAnswerSerializer(many=True)

    class Meta:
        model = ProfileQuestion
        fields = ['order', 'question', 'answers', 'id']

    def validate(self, attrs):
        if not confusable_homoglyphs_check(attrs):
            raise serializers.ValidationError(HOMOGLYPH_ERROR)
        return super().validate(attrs)


class ProfileResponseSerializer(ObjectPermissionsAssignmentMixin,
                                serializers.ModelSerializer):
    submitted_by = serializers.SlugRelatedField(
        slug_field='email', queryset=User.objects.all(),
        default=serializers.CurrentUserDefault())
    question = serializers.PrimaryKeyRelatedField(
        queryset=ProfileQuestion.objects.filter(active=True))
    selected = serializers.PrimaryKeyRelatedField(
        queryset=ProfileAnswer.objects.all())

    class Meta:
        model = ProfileResponse
        fields = ['submitted_by', 'question', 'selected', 'id']
        validators = [UniqueTogetherValidator(ProfileResponse.objects.all(), [
                                              'submitted_by', 'question',])]

    def get_permissions_map(self, created):
        perms = {}
        if not created:
            submitted_by = self.instance.submitted_by
            perms = {
                'view_profileresponse': [submitted_by,],
                'change_profileresponse': [submitted_by,],
                'delete_profileresponse': [submitted_by,]
            }

        return perms

    def validate(self, attrs):
        """
        check question and selected relationship
        """
        if not confusable_homoglyphs_check(attrs):
            raise serializers.ValidationError(HOMOGLYPH_ERROR)
        if not attrs['question'].answers.contains(attrs['selected']):
            raise serializers.ValidationError(
                "selected answer must be for the selected question")
        return attrs


class MiniCandidateRankingSerializer(serializers.ModelSerializer):
    candidate = serializers.SlugRelatedField(
        slug_field='email', queryset=User.objects.all())

    class Meta:
        model = CandidateRanking
        fields = ['id', 'rank', 'candidate',]

    def validate(self, attrs):
        if not confusable_homoglyphs_check(attrs):
            raise serializers.ValidationError(HOMOGLYPH_ERROR)
        return super().validate(attrs)


class CandidateListSerializer(serializers.ModelSerializer,
                              ObjectPermissionsAssignmentMixin):
    ranker = serializers.SlugRelatedField(
        slug_field='email', queryset=User.objects.all(),
        default=serializers.CurrentUserDefault())
    role = serializers.PrimaryKeyRelatedField(
        queryset=Vacancy.objects.all(), required=False)
    competency = serializers.PrimaryKeyRelatedField(
        queryset=Job.objects.all(), required=False)
    rankings = MiniCandidateRankingSerializer(many=True, read_only=True)

    class Meta:
        model = CandidateList
        fields = ['id', 'ranker', 'name', 'role',
                  'competency', 'rankings', 'modified', 'created',]
        extra_kwargs = {'modified': {'read_only': True},
                        'created': {'read_only': True}}

    def get_permissions_map(self, created):
        perms = {}
        if not created:
            submitted_by = self.instance.ranker
            perms = {
                'view_candidatelist': [submitted_by,],
                'change_candidatelist': [submitted_by,],
                'delete_candidatelist': [submitted_by,]
            }

        return perms

    def validate(self, attrs):
        if not confusable_homoglyphs_check(attrs):
            raise serializers.ValidationError(HOMOGLYPH_ERROR)
        return super().validate(attrs)


class CandidateRankingSerializer(serializers.ModelSerializer,
                                 ObjectPermissionsAssignmentMixin):
    candidate_list = serializers.PrimaryKeyRelatedField(
        queryset=CandidateList.objects.all())
    candidate = serializers.SlugRelatedField(
        slug_field='email', queryset=User.objects.all())

    class Meta:
        model = CandidateRanking
        fields = ['id', 'candidate_list', 'rank',
                  'candidate', 'modified', 'created',]
        extra_kwargs = {'modified': {'read_only': True},
                        'created': {'read_only': True}}

    def get_permissions_map(self, created):
        perms = {}
        if not created:
            submitted_by = self.instance.candidate_list.ranker
            perms = {
                'view_candidateranking': [submitted_by,],
                'change_candidateranking': [submitted_by,],
                'delete_candidateranking': [submitted_by,]
            }

        return perms

    def validate(self, attrs):
        if not confusable_homoglyphs_check(attrs):
            raise serializers.ValidationError(HOMOGLYPH_ERROR)
        return super().validate(attrs)


class TrainingPlanSerializer(serializers.ModelSerializer,
                             ObjectPermissionsAssignmentMixin):
    planner = serializers.SlugRelatedField(
        slug_field='email', queryset=User.objects.all(),
        default=serializers.CurrentUserDefault())
    role = serializers.PrimaryKeyRelatedField(
        queryset=Job.objects.all())
    trainee = serializers.SlugRelatedField(
        slug_field='email', queryset=User.objects.all())

    class Meta:
        model = TrainingPlan
        fields = ['id', 'role', 'planner', 'trainee', 'modified', 'created',]
        extra_kwargs = {'modified': {'read_only': True},
                        'created': {'read_only': True}}

    def get_permissions_map(self, created):
        perms = {}
        if not created:
            submitted_by = self.instance.planner
            perms = {
                'view_trainingplan': [submitted_by,],
                'change_trainingplan': [submitted_by,],
                'delete_trainingplan': [submitted_by,]
            }

        return perms

    def validate(self, attrs):
        if not confusable_homoglyphs_check(attrs):
            raise serializers.ValidationError(HOMOGLYPH_ERROR)
        return super().validate(attrs)
