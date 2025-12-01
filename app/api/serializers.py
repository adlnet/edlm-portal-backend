import logging

from django.db import transaction
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from rest_framework_guardian.serializers import \
    ObjectPermissionsAssignmentMixin

from api.models import (CandidateList, CandidateRanking, ProfileAnswer,
                        ProfileQuestion, ProfileResponse, TrainingPlan,
                        LearningPlan, LearningPlanCompetency, LearningPlanGoal,
                        LearningPlanGoalCourse, LearningPlanGoalKsa)
from configuration.utils.portal_utils import confusable_homoglyphs_check
from external.models import Competency, Course, Job, Ksa
from external.utils.eccr_utils import validate_eccr_item
from external.utils.elrr_utils import (create_elrr_goal,
                                       get_or_create_elrr_person_by_email,
                                       build_goal_data_for_elrr,
                                       store_ksa_to_elrr_goal,
                                       store_course_to_elrr_goal,
                                       sync_goal_updates_to_elrr)
from external.utils.xds_utils import validate_xds_course
from users.models import User
from vacancies.models import Vacancy

logger = logging.getLogger(__name__)
HOMOGLYPH_ERROR = "Data contains homoglyphs and can be dangerous. Check" + \
    " logs for more details"
ECCR_FAILED_ERROR = "Failed to validate ECCR item: "
ECCR_EXCEPTION_MSG = "ECCR validation failed, please check logs for details"
XDS_FAILED_ERROR = "Failed to validate XDS item: "
XDS_EXCEPTION_MSG = "XDS validation failed, please check logs for details"
PARENT_ID_UPDATE_ERROR = "Cannot change the parent id"
ELRR_SYNC_ERROR = "Failed to sync with ELRR, please check logs for details"


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


class LearningPlanGoalCourseSerializer(serializers.ModelSerializer,
                                       ObjectPermissionsAssignmentMixin):
    plan_goal = serializers.PrimaryKeyRelatedField(
        queryset=LearningPlanGoal.objects.all())
    course_external_reference = serializers.CharField(
        write_only=True, required=True
    )
    # Read-only field showing the actual linked XDS Course reference
    xds_course = serializers.PrimaryKeyRelatedField(
        read_only=True
    )
    course_name = serializers.ReadOnlyField()

    class Meta:
        model = LearningPlanGoalCourse
        fields = ['id', 'plan_goal', 'course_name',
                  'course_external_reference',
                  'xds_course', 'modified', 'created',]
        extra_kwargs = {'modified': {'read_only': True},
                        'created': {'read_only': True}}

    def create(self, validated_data):
        """
        Create or link to XDS External Course
        based on external reference
        """
        if 'course_external_reference' in validated_data:
            reference = validated_data.pop('course_external_reference')
            course = Course.objects.filter(reference=reference).first()

            if course is None:
                try:
                    course_name = validate_xds_course(reference)
                    course = Course.objects.create(
                        reference=reference,
                        name=course_name
                    )
                except Exception as e:
                    logger.error(f"{XDS_FAILED_ERROR} {e}")
                    raise serializers.ValidationError(
                        XDS_EXCEPTION_MSG
                    )
            validated_data['xds_course'] = course

        with transaction.atomic():
            learning_plan_goal_course = LearningPlanGoalCourse.objects.create(
                **validated_data
            )

            # Store to ELRR and store the returned ID
            goal = learning_plan_goal_course.plan_goal
            if goal.elrr_goal_id:
                try:
                    elrr_learning_resource_id = store_course_to_elrr_goal(
                        learning_plan_goal_course,
                        str(goal.elrr_goal_id)
                    )

                    # Store the ELRR learning resource ID
                    learning_plan_goal_course.elrr_course_id = \
                        elrr_learning_resource_id
                    learning_plan_goal_course.save(
                        update_fields=['elrr_course_id'])

                except (ConnectionError, ValueError) as e:
                    logger.error(f'Failed to store course to ELRR: {e}')
                    raise serializers.ValidationError(
                        ELRR_SYNC_ERROR
                    )

        return learning_plan_goal_course

    def update(self, instance, validated_data):
        """
        Update based on external reference and
        sync to ELRR if course updated
        """
        goal = instance.plan_goal

        if 'plan_goal' in validated_data:
            new_goal = validated_data['plan_goal']
            if goal != new_goal:
                raise serializers.ValidationError(PARENT_ID_UPDATE_ERROR)

        course_changed = False
        if 'course_external_reference' in validated_data:
            reference = validated_data.pop('course_external_reference')
            old_elrr_course_id = instance.elrr_course_id
            old_course = instance.xds_course
            course = Course.objects.filter(reference=reference).first()

            if course is None:
                try:
                    course_name = validate_xds_course(reference)
                    course = Course.objects.create(
                        reference=reference,
                        name=course_name
                    )
                except Exception as e:
                    logger.error(f"{XDS_FAILED_ERROR} {e}")
                    raise serializers.ValidationError(XDS_EXCEPTION_MSG)

            validated_data['xds_course'] = course

            if old_course != course:
                course_changed = True

        with transaction.atomic():
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

            if course_changed and goal.elrr_goal_id:
                try:
                    elrr_learning_resource_id = store_course_to_elrr_goal(
                        instance,
                        str(goal.elrr_goal_id),
                        str(old_elrr_course_id)
                    )
                    instance.elrr_course_id = elrr_learning_resource_id
                    instance.save(update_fields=['elrr_course_id'])
                except (ConnectionError, ValueError) as e:
                    logger.error(f'Failed to add new course to ELRR: {e}')
                    raise serializers.ValidationError(
                        ELRR_SYNC_ERROR
                    )

        return instance

    def get_permissions_map(self, created):
        perms = {}
        if not created:
            submitted_by = (self.instance.plan_goal.plan_competency
                            .learning_plan.learner)
            perms = {
                'view_learningplangoalcourse': [submitted_by,],
                'change_learningplangoalcourse': [submitted_by,],
                'delete_learningplangoalcourse': [submitted_by,]
            }
        return perms

    def validate(self, attrs):
        if not confusable_homoglyphs_check(attrs):
            raise serializers.ValidationError(HOMOGLYPH_ERROR)
        return super().validate(attrs)


class LearningPlanGoalCourseReadSerializer(serializers.ModelSerializer):
    """
    Nested serializer for displaying Read-Only
    Courses with Learning Plan Goals
    """
    class Meta:
        model = LearningPlanGoalCourse
        fields = ['id', 'course_name', 'xds_course']


class LearningPlanGoalKsaSerializer(serializers.ModelSerializer,
                                    ObjectPermissionsAssignmentMixin):
    plan_goal = serializers.PrimaryKeyRelatedField(
        queryset=LearningPlanGoal.objects.all())
    # Input only fields for external KSA
    ksa_external_reference = serializers.CharField(
        write_only=True, required=True
    )
    # Read-only field showing the actual linked ECCR KSA Id
    eccr_ksa = serializers.PrimaryKeyRelatedField(
        read_only=True
    )
    ksa_name = serializers.ReadOnlyField()

    class Meta:
        model = LearningPlanGoalKsa
        fields = ['id', 'plan_goal', 'ksa_external_reference',
                  'ksa_name', 'eccr_ksa', 'current_proficiency',
                  'target_proficiency', 'modified', 'created',]
        extra_kwargs = {'modified': {'read_only': True},
                        'created': {'read_only': True}}

    def create(self, validated_data):
        """
        Create or link to ECCR External KSA
        based on external reference
        """
        if 'ksa_external_reference' in validated_data:
            reference = validated_data.pop('ksa_external_reference')
            ksa = Ksa.objects.filter(reference=reference).first()

            if ksa is None:
                try:
                    ksa_name = validate_eccr_item(reference)
                    ksa = Ksa.objects.create(
                        reference=reference,
                        name=ksa_name
                    )
                except Exception as e:
                    logger.error(f"{ECCR_FAILED_ERROR} {e}")
                    raise serializers.ValidationError(
                        ECCR_EXCEPTION_MSG
                    )
            validated_data['eccr_ksa'] = ksa

        with transaction.atomic():
            learning_plan_goal_ksa = LearningPlanGoalKsa.objects.create(
                **validated_data
            )

            goal = learning_plan_goal_ksa.plan_goal
            if goal.elrr_goal_id:
                try:
                    elrr_competency_id = store_ksa_to_elrr_goal(
                        learning_plan_goal_ksa,
                        str(goal.elrr_goal_id)
                    )

                    # Store the ELRR competency ID
                    learning_plan_goal_ksa.elrr_ksa_id = elrr_competency_id
                    learning_plan_goal_ksa.save(update_fields=['elrr_ksa_id'])

                except (ConnectionError, ValueError) as e:
                    logger.error(f'Failed to store KSA to ELRR: {e}')
                    raise serializers.ValidationError(
                        ELRR_SYNC_ERROR
                    )

        return learning_plan_goal_ksa

    def update(self, instance, validated_data):
        """Update based on external reference"""
        goal = instance.plan_goal

        if 'plan_goal' in validated_data:
            new_goal = validated_data['plan_goal']
            if goal != new_goal:
                raise serializers.ValidationError(PARENT_ID_UPDATE_ERROR)

        ksa_changed = False
        if 'ksa_external_reference' in validated_data:
            reference = validated_data.pop('ksa_external_reference')
            old_elrr_ksa_id = instance.elrr_ksa_id
            old_ksa = instance.eccr_ksa

            ksa = Ksa.objects.filter(reference=reference).first()
            if ksa is None:
                try:
                    ksa_name = validate_eccr_item(reference)
                    ksa = Ksa.objects.create(
                        reference=reference,
                        name=ksa_name
                    )
                except Exception as e:
                    logger.error(f"{ECCR_FAILED_ERROR} {e}")
                    raise serializers.ValidationError(ECCR_EXCEPTION_MSG)

            validated_data['eccr_ksa'] = ksa

            if old_ksa != ksa:
                ksa_changed = True

        with transaction.atomic():
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

            if ksa_changed and goal.elrr_goal_id:
                try:
                    elrr_competency_id = store_ksa_to_elrr_goal(
                        instance,
                        str(goal.elrr_goal_id),
                        str(old_elrr_ksa_id)
                    )
                    instance.elrr_ksa_id = elrr_competency_id
                    instance.save(update_fields=['elrr_ksa_id'])
                except (ConnectionError, ValueError) as e:
                    logger.error(f'Failed to add new KSA to ELRR: {e}')
                    raise serializers.ValidationError(
                        ELRR_SYNC_ERROR
                    )

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
    # Nested read-only Courses
    courses = LearningPlanGoalCourseReadSerializer(
        many=True, read_only=True)

    class Meta:
        model = LearningPlanGoal
        fields = ['id', 'plan_competency', 'goal_name', 'timeline',
                  'resources_support', 'obstacles', 'resources_support_other',
                  'obstacles_other', 'ksas', 'courses',
                  'modified', 'created']
        extra_kwargs = {'modified': {'read_only': True},
                        'created': {'read_only': True}}

    def create(self, validated_data):
        """
        Create LearningPlanGoal and store to ELRR
        """
        with transaction.atomic():
            learning_plan_goal = LearningPlanGoal.objects.create(
                **validated_data)
            learner = learning_plan_goal.plan_competency.learning_plan.learner

            try:
                person_id = get_or_create_elrr_person_by_email(learner)

                goal_data = build_goal_data_for_elrr(
                    learning_plan_goal,
                    person_id
                )

                elrr_resp = create_elrr_goal(goal_data)

                learning_plan_goal.elrr_goal_id = elrr_resp['id']
                learning_plan_goal.save(update_fields=['elrr_goal_id'])

            except (ConnectionError, ValueError) as e:
                logger.error(f'Failed to create ELRR goal: {e}')
                raise serializers.ValidationError(
                    ELRR_SYNC_ERROR
                )

        return learning_plan_goal

    def update(self, instance, validated_data):
        """
        Update and check if a user is trying to change the parent id
        """
        if 'plan_competency' in validated_data:
            new_competency = validated_data['plan_competency']
            if instance.plan_competency != new_competency:
                raise serializers.ValidationError(
                    PARENT_ID_UPDATE_ERROR
                )

        with transaction.atomic():
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

            if instance.elrr_goal_id:
                try:
                    sync_goal_updates_to_elrr(instance, validated_data.keys())
                except (ConnectionError, ValueError) as e:
                    logger.error(f'Failed to sync goal updates to ELRR: {e}')
                    raise serializers.ValidationError(
                        ELRR_SYNC_ERROR
                    )

        return instance

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
    courses = LearningPlanGoalCourseReadSerializer(
        many=True, read_only=True)

    class Meta:
        model = LearningPlanGoal
        fields = ['id', 'goal_name', 'timeline',
                  'resources_support', 'obstacles',
                  'resources_support_other',
                  'obstacles_other', 'ksas', 'courses',
                  'elrr_goal_id']


class LearningPlanCompetencySerializer(serializers.ModelSerializer,
                                       ObjectPermissionsAssignmentMixin):
    learning_plan = serializers.PrimaryKeyRelatedField(
        queryset=LearningPlan.objects.all())
    # Input only fields for creating or linking to external Competency
    competency_external_reference = serializers.CharField(
        write_only=True, required=True
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
                  'competency_external_reference', 'eccr_competency',
                  'priority', 'goals', 'modified', 'created',]
        extra_kwargs = {'modified': {'read_only': True},
                        'created': {'read_only': True}}

    def create(self, validated_data):
        """
        Create or link to ECCR External Competency
        based on external reference
        """
        if 'competency_external_reference' in validated_data:
            reference = validated_data.pop('competency_external_reference')
            competency = Competency.objects.filter(reference=reference).first()

            if competency is None:
                try:
                    comp_name = validate_eccr_item(reference)
                    competency = Competency.objects.create(
                        reference=reference,
                        name=comp_name
                    )
                except Exception as e:
                    logger.error(f"{ECCR_FAILED_ERROR} {e}")
                    raise serializers.ValidationError(
                        ECCR_EXCEPTION_MSG
                    )
            validated_data['eccr_competency'] = competency

        learning_plan_competency = LearningPlanCompetency.objects.create(
            **validated_data
        )

        return learning_plan_competency

    def update(self, instance, validated_data):
        """
        Update based on external reference
        """
        if 'learning_plan' in validated_data:
            new_plan = validated_data['learning_plan']
            if instance.learning_plan != new_plan:
                raise serializers.ValidationError(
                    PARENT_ID_UPDATE_ERROR
                )

        if 'competency_external_reference' in validated_data:
            reference = validated_data.pop('competency_external_reference')
            competency = Competency.objects.filter(reference=reference).first()

            if competency is None:
                try:
                    comp_name = validate_eccr_item(reference)
                    competency = Competency.objects.create(
                        reference=reference,
                        name=comp_name
                    )
                except Exception as e:
                    logger.error(f"{ECCR_FAILED_ERROR} {e}")
                    raise serializers.ValidationError(
                        ECCR_EXCEPTION_MSG
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
        slug_field='email',
        default=serializers.CurrentUserDefault(),
        read_only=True)
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

    def create(self, validated_data):
        validated_data['learner'] = self.context['request'].user
        return super().create(validated_data)

    def validate(self, attrs):
        if not confusable_homoglyphs_check(attrs):
            raise serializers.ValidationError(HOMOGLYPH_ERROR)
        return super().validate(attrs)
