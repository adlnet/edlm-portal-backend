import logging

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from rest_framework_guardian.serializers import \
    ObjectPermissionsAssignmentMixin

from api.models import ProfileAnswer, ProfileQuestion, ProfileResponse
from users.models import User

logger = logging.getLogger(__name__)


class ProfileAnswerSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProfileAnswer
        fields = ['order', 'answer', 'id']


class ProfileQuestionSerializer(serializers.ModelSerializer):
    answers = ProfileAnswerSerializer(many=True)

    class Meta:
        model = ProfileQuestion
        fields = ['order', 'question', 'answers', 'id']


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
        if not attrs['question'].answers.contains(attrs['selected']):
            raise serializers.ValidationError(
                "selected answer must be for the selected question")
        return attrs
