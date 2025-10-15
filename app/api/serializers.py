import logging

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from rest_framework_guardian.serializers import \
    ObjectPermissionsAssignmentMixin

from api.models import (CandidateList, CandidateRanking, ProfileAnswer,
                        ProfileQuestion, ProfileResponse, TrainingPlan,
                        LearningPlan, LearningPlanCompetency, LearningPlanGoal,
                        LearningPlanGoalKsa)
from configuration.utils.portal_utils import confusable_homoglyphs_check
from external.models import Competency, Job, Ksa
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


class LearningPlanGoalKsaSerializer(serializers.ModelSerializer,
                                    ObjectPermissionsAssignmentMixin):
    plan_goal = serializers.PrimaryKeyRelatedField(
        queryset=LearningPlanGoal.objects.all())
    # Input only fields for external KSA
    ksa_external_reference = serializers.CharField(
        write_only=True, required=False
    )
    ksa_external_name = serializers.CharField(
        write_only=True, required=False
    )
    # Read-only field showing the actual linked ECCR KSA Id and name
    eccr_ksa = serializers.PrimaryKeyRelatedField(
        read_only=True
    )
    ksa_name = serializers.ReadOnlyField()

    class Meta:
        model = LearningPlanGoalKsa
        fields = ['id', 'plan_goal', 'ksa_external_reference',
                  'ksa_external_name', 'ksa_name', 'eccr_ksa',
                  'current_proficiency', 'target_proficiency',
                  'modified', 'created',]
        extra_kwargs = {'modified': {'read_only': True},
                        'created': {'read_only': True}}

    def create(self, validated_data):
        """
        Create or link to ECCR External KSA
        based on external reference/name
        """
        ksa_data = {}
        if 'ksa_external_reference' in validated_data and \
           'ksa_external_name' in validated_data:
            ksa_data = {
                'reference': validated_data.pop('ksa_external_reference'),
                'name': validated_data.pop('ksa_external_name')
            }

        if ksa_data:
            ksa, created = Ksa.objects.get_or_create(
                reference=ksa_data['reference'],
                defaults=ksa_data
            )
            validated_data['eccr_ksa'] = ksa

        learning_plan_goal_ksa = LearningPlanGoalKsa.objects.create(
            **validated_data
        )

        return learning_plan_goal_ksa

    def update(self, instance, validated_data):
        """
        Update based on external reference/name
        """
        ksa_data = {}
        if 'ksa_external_reference' in validated_data and \
           'ksa_external_name' in validated_data:
            ksa_data = {
                'reference': validated_data.pop('ksa_external_reference'),
                'name': validated_data.pop('ksa_external_name')
            }

        if ksa_data:
            ksa, created = Ksa.objects.get_or_create(
                reference=ksa_data['reference'],
                defaults=ksa_data
            )
            validated_data['eccr_ksa'] = ksa

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

    def get_permissions_map(self, created):
        perms = {}
        if not created:
            submitted_by = (self.instance.plan_goal.plan_competency
                            .learning_plan.learner)
            perms = {
                'view_learningplangoalksa': [submitted_by,],
                'change_learningplangoalksa': [submitted_by,],
                'delete_learningplangoalksa': [submitted_by,]
            }
        return perms

    def validate(self, attrs):
        if not confusable_homoglyphs_check(attrs):
            raise serializers.ValidationError(HOMOGLYPH_ERROR)
        return super().validate(attrs)


class LearningPlanGoalKsaReadSerializer(serializers.ModelSerializer):
    """
    Nested serializer for displaying Read-Only
    KSAs with Learning Plan Goals
    """
    class Meta:
        model = LearningPlanGoalKsa
        fields = ['id', 'ksa_name', 'eccr_ksa', 'current_proficiency',
                  'target_proficiency']


class LearningPlanGoalSerializer(serializers.ModelSerializer,
                                 ObjectPermissionsAssignmentMixin):
    plan_competency = serializers.PrimaryKeyRelatedField(
        queryset=LearningPlanCompetency.objects.all())
    # Nested read-only KSAs
    ksas = LearningPlanGoalKsaReadSerializer(many=True, read_only=True)

    class Meta:
        model = LearningPlanGoal
        fields = ['id', 'plan_competency', 'goal_name', 'timeline',
                  'resources_support', 'obstacles', 'resources_support_other',
                  'obstacles_other', 'ksas', 'modified', 'created']
        extra_kwargs = {'modified': {'read_only': True},
                        'created': {'read_only': True}}

    def get_permissions_map(self, created):
        perms = {}
        if not created:
            submitted_by = self.instance.plan_competency.learning_plan.learner
            perms = {
                'view_learningplangoal': [submitted_by,],
                'change_learningplangoal': [submitted_by,],
                'delete_learningplangoal': [submitted_by,]
            }
        return perms

    def validate(self, attrs):
        if not confusable_homoglyphs_check(attrs):
            raise serializers.ValidationError(HOMOGLYPH_ERROR)
        return super().validate(attrs)


class LearningPlanGoalReadSerializer(serializers.ModelSerializer):
    """
    Nested serializer for displaying Read-Only
    Goals with Learning Plan Competencies
    """
    ksas = LearningPlanGoalKsaReadSerializer(
        many=True, read_only=True)

    class Meta:
        model = LearningPlanGoal
        fields = ['id', 'goal_name', 'timeline',
                  'resources_support', 'obstacles',
                  'resources_support_other',
                  'obstacles_other', 'ksas']


class LearningPlanCompetencySerializer(serializers.ModelSerializer,
                                       ObjectPermissionsAssignmentMixin):
    learning_plan = serializers.PrimaryKeyRelatedField(
        queryset=LearningPlan.objects.all())
    # Input only fields for creating or linking to external Competency
    competency_external_reference = serializers.CharField(
        write_only=True, required=False
    )
    competency_external_name = serializers.CharField(
        write_only=True, required=False
    )
    # Read-only field showing the actual linked ECCR Competency Id and name
    eccr_competency = serializers.PrimaryKeyRelatedField(
        read_only=True
    )
    plan_competency_name = serializers.ReadOnlyField()
    goals = LearningPlanGoalReadSerializer(many=True, read_only=True)

    class Meta:
        model = LearningPlanCompetency
        fields = ['id', 'learning_plan', 'plan_competency_name',
                  'competency_external_reference', 'competency_external_name',
                  'eccr_competency', 'priority', 'goals',
                  'modified', 'created',]
        extra_kwargs = {'modified': {'read_only': True},
                        'created': {'read_only': True}}

    def create(self, validated_data):
        """
        Create or link to ECCR External Competency
        based on external reference/name
        """
        competency_data = {}
        if 'competency_external_reference' in validated_data and \
           'competency_external_name' in validated_data:
            competency_data = {
                'reference': validated_data.pop(
                    'competency_external_reference'),
                'name': validated_data.pop(
                    'competency_external_name')
            }

        if competency_data:
            competency, created = Competency.objects.get_or_create(
                reference=competency_data['reference'],
                defaults=competency_data
            )
            validated_data['eccr_competency'] = competency

        learning_plan_competency = LearningPlanCompetency.objects.create(
            **validated_data
        )

        return learning_plan_competency

    def update(self, instance, validated_data):
        """
        Update based on external reference/name
        """
        competency_data = {}
        if 'competency_external_reference' in validated_data and \
           'competency_external_name' in validated_data:
            competency_data = {
                'reference': validated_data.pop(
                    'competency_external_reference'),
                'name': validated_data.pop(
                    'competency_external_name')
            }

        if competency_data:
            competency, created = Competency.objects.get_or_create(
                reference=competency_data['reference'],
                defaults=competency_data
            )
            validated_data['eccr_competency'] = competency

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

    def get_permissions_map(self, created):
        perms = {}
        if not created:
            submitted_by = self.instance.learning_plan.learner
            perms = {
                'view_learningplancompetency': [submitted_by,],
                'change_learningplancompetency': [submitted_by,],
                'delete_learningplancompetency': [submitted_by,]
            }
        return perms

    def validate(self, attrs):
        if not confusable_homoglyphs_check(attrs):
            raise serializers.ValidationError(HOMOGLYPH_ERROR)
        return super().validate(attrs)


class LearningPlanCompetencyReadSerializer(serializers.ModelSerializer):
    """
    Nested serializer for displaying Read-Only
    Competencies with Learning Plans
    """
    goals = LearningPlanGoalReadSerializer(many=True, read_only=True)

    class Meta:
        model = LearningPlanCompetency
        fields = ['id', 'plan_competency_name',
                  'eccr_competency', 'priority', 'goals',]


class LearningPlanSerializer(serializers.ModelSerializer,
                             ObjectPermissionsAssignmentMixin):
    learner = serializers.SlugRelatedField(
        slug_field='email', queryset=User.objects.all(),
        default=serializers.CurrentUserDefault())
    competencies = LearningPlanCompetencyReadSerializer(
        many=True, read_only=True)

    class Meta:
        model = LearningPlan
        fields = ['id', 'learner', 'name', 'timeframe',
                  'competencies', 'modified', 'created',]
        extra_kwargs = {'modified': {'read_only': True},
                        'created': {'read_only': True}}

    def get_permissions_map(self, created):
        perms = {}
        if not created:
            submitted_by = self.instance.learner
            perms = {
                'view_learningplan': [submitted_by,],
                'change_learningplan': [submitted_by,],
                'delete_learningplan': [submitted_by,]
            }
        return perms

    def validate(self, attrs):
        if not confusable_homoglyphs_check(attrs):
            raise serializers.ValidationError(HOMOGLYPH_ERROR)
        return super().validate(attrs)
