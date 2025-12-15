import uuid

from django.contrib.postgres.fields import ArrayField
from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse
from model_utils import Choices
from model_utils.models import TimeStampedModel

from external.models import Competency, Course, Job, Ksa
from portal.regex import REGEX_CHECK, REGEX_ERROR_MESSAGE
from users.models import User
from vacancies.models import Vacancy


# Create your models here.
class ProfileQuestion(models.Model):
    active = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(unique=True)
    question = models.TextField(unique=True, validators=[
        RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
    ])

    class Meta:
        ordering = ['order',]

    def __str__(self):
        return f'{self.order}. {self.question}'

    def get_absolute_url(self):
        return reverse("api:profile-questions-detail", kwargs={"pk": self.pk})


class ProfileAnswer(models.Model):
    question = models.ForeignKey(
        ProfileQuestion, on_delete=models.CASCADE, related_name='answers')
    order = models.PositiveSmallIntegerField()
    answer = models.TextField(validators=[
        RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
    ])

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['question', 'order',],
                name='unique_answer_order'),
            models.UniqueConstraint(
                fields=['question', 'answer'],
                name='unique_question_answer')
        ]
        ordering = ['order',]

    def __str__(self):
        return f'{self.order}. {self.answer}'


class ProfileResponse(TimeStampedModel):
    question = models.ForeignKey(
        ProfileQuestion, on_delete=models.CASCADE, related_name='responses')
    submitted_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='responses')
    selected = models.ForeignKey(
        ProfileAnswer, on_delete=models.CASCADE, related_name='responses')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['question', 'submitted_by',],
                name='unique_question_response')
        ]

    def get_absolute_url(self):
        return reverse("api:profile-responses-detail", kwargs={"pk": self.pk})


class CandidateList(TimeStampedModel):
    ranker = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='lists')
    name = models.TextField(validators=[
        RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
    ])
    role = models.ForeignKey(
        Vacancy, on_delete=models.CASCADE, related_name='recommended',
        null=True, blank=True)
    competency = models.ForeignKey(
        Job, on_delete=models.CASCADE, related_name='recommended',
        null=True, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(role__isnull=True) ^ models.Q(
                    competency__isnull=True), name="role_or_competency")
        ]

    def __str__(self):
        return f'{self.name} - {self.role if self.competency is None
                                else self.competency} ({self.ranker})'

    def get_absolute_url(self):
        return reverse("api:candidate-lists-detail", kwargs={"pk": self.pk})


class CandidateRanking(TimeStampedModel):
    candidate_list = models.ForeignKey(
        CandidateList, on_delete=models.CASCADE, related_name='rankings')
    candidate = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='rankings')
    rank = models.PositiveSmallIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['candidate_list', 'rank',],
                name='unique_list_ranks'),
            models.UniqueConstraint(
                fields=['candidate_list', 'candidate'],
                name='unique_candidates_in_list')
        ]
        ordering = ['rank',]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.candidate_list.save(update_fields=['modified',])

    def __str__(self):
        return f'{self.rank}. {self.candidate} in {self.candidate_list}'

    def get_absolute_url(self):
        return reverse("api:candidate-rankings-detail", kwargs={"pk": self.pk})


class TrainingPlan(TimeStampedModel):
    trainee = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='training_plans_for_me')
    planner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='training_plans_by_me')
    role = models.ForeignKey(
        Job, on_delete=models.CASCADE, related_name='training_plans',
        null=True, blank=True)

    def get_absolute_url(self):
        return reverse("api:training-plans-detail", kwargs={"pk": self.pk})


class LearningPlan(TimeStampedModel):
    """Model to store learning plans detail"""
    TIMEFRAME_CHOICES = Choices('Short-term (1-2 years)',
                                'Long-term (3-4 years)')
    learner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='learning_plans')
    name = models.TextField(validators=[
        RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
    ])
    timeframe = models.CharField(max_length=50, choices=TIMEFRAME_CHOICES)

    def __str__(self):
        return f'{self.name} - {self.learner} ({self.timeframe})'

    def get_absolute_url(self):
        return reverse("api:learning-plans-detail", kwargs={"pk": self.pk})


class LearningPlanCompetency(TimeStampedModel):
    """Model to store competencies for a learning plan"""
    PRIORITY_CHOICES = Choices('Highest', 'High', 'Medium', 'Low', 'Lowest')
    learning_plan = models.ForeignKey(
        LearningPlan, on_delete=models.CASCADE, related_name='competencies')
    eccr_competency = models.ForeignKey(
        Competency, on_delete=models.CASCADE,
        related_name='learning_plans_competencies')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.learning_plan.save(update_fields=['modified',])

    # Return the name of the competency
    @property
    def plan_competency_name(self):
        return self.eccr_competency.name

    def __str__(self):
        return (f'{self.plan_competency_name} - '
                f'{self.learning_plan} ({self.priority})')

    def get_absolute_url(self):
        return reverse("api:learning-plan-competencies-detail",
                       kwargs={"pk": self.pk})


class LearningPlanGoal(TimeStampedModel):
    """Model to store goals for a learning plan"""
    class TimeLineChoices(models.IntegerChoices):
        MONTHS_3 = 3, '1-3 months'
        MONTHS_6 = 6, '3-6 months'
        MONTHS_9 = 9, '6-9 months'
        MONTHS_12 = 12, '9-12 months'
        MONTHS_18 = 18, '12-18 months'
        MONTHS_24 = 24, '18-24 months'
        MONTHS_30 = 30, '2-2.5 years'
        MONTHS_36 = 36, '2.5-3 years'
        MONTHS_42 = 42, '3-3.5 years'
        MONTHS_48 = 48, '3.5-4 years'
        MONTHS_54 = 54, '4-4.5 years'
        MONTHS_60 = 60, '4.5-5 years'

    plan_competency = models.ForeignKey(
        LearningPlanCompetency, on_delete=models.CASCADE, related_name='goals')
    goal_name = models.TextField(validators=[
        RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
    ])
    timeline = models.IntegerField(choices=TimeLineChoices.choices)

    # store a list of selected choices
    resources_support = ArrayField(
        models.CharField(
            max_length=500,
            validators=[RegexValidator(
                regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE)],
        ),
        default=list,
        blank=True,
    )

    obstacles = ArrayField(
        models.CharField(
            max_length=500,
            validators=[RegexValidator(
                regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE)],
        ),
        default=list,
        blank=True,
    )

    resources_support_other = models.TextField(blank=True, validators=[
        RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
    ])
    obstacles_other = models.TextField(blank=True, validators=[
        RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
    ])

    elrr_goal_id = models.UUIDField(
        null=True, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.plan_competency.save(update_fields=['modified',])

    def __str__(self):
        return f'{self.goal_name} - {self.plan_competency} ({self.timeline})'

    def get_absolute_url(self):
        return reverse("api:learning-plan-goals-detail",
                       kwargs={"pk": self.pk})


class LearningPlanGoalKsa(TimeStampedModel):
    """Model to store KSAs for a learning plan goal"""
    plan_goal = models.ForeignKey(
        LearningPlanGoal, on_delete=models.CASCADE, related_name='ksas')
    eccr_ksa = models.ForeignKey(
        Ksa, on_delete=models.CASCADE, related_name='learning_plans_ksas')
    current_proficiency = models.CharField(max_length=20, validators=[
        RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
    ])
    target_proficiency = models.CharField(max_length=20, validators=[
        RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
    ])
    elrr_ksa_id = models.UUIDField(
        null=True, blank=True)

    # Return the name of the KSA
    @property
    def ksa_name(self):
        return self.eccr_ksa.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.plan_goal.save(update_fields=['modified',])

    def __str__(self):
        return (f'{self.ksa_name} - {self.plan_goal}'
                f'({self.current_proficiency} - {self.target_proficiency})')

    def get_absolute_url(self):
        return reverse("api:learning-plan-goal-ksas-detail",
                       kwargs={"pk": self.pk})


class LearningPlanGoalCourse(TimeStampedModel):
    """Model to store courses for a learning plan goal"""
    plan_goal = models.ForeignKey(
        LearningPlanGoal, on_delete=models.CASCADE, related_name='courses')
    xds_course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='xds_courses')
    elrr_course_id = models.UUIDField(
        null=True, blank=True)

    # Return the name of the course
    @property
    def course_name(self):
        return self.xds_course.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.plan_goal.save(update_fields=['modified',])

    def __str__(self):
        return f'{self.course_name} - {self.plan_goal}'

    def get_absolute_url(self):
        return reverse("api:learning-plan-goal-courses-detail",
                       kwargs={"pk": self.pk})


# SAPRO Application Models section
class Application(TimeStampedModel):
    """
    Main application model for SAPR certification applications.
    Supports both NEW and RENEWAL application types.
    """

    class ApplicationChoices(models.TextChoices):
        NEW = 'new', 'New Application'
        RENEWAL = 'renewal', 'Renewal Application'

    class PositionChoices(models.TextChoices):
        SAPR_VA = 'SAPR_VA', 'SAPR VA (Victim Advocate)'
        SARC_SAPR_PM = 'SARC/SAPR_PM', 'SARC / SAPR PM'

    class StatusChoices(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        SUBMITTED = 'submitted', 'Submitted'
        UNDER_REVIEW = 'under_review', 'Under Review'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    # Foreign Key
    applicant = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='applications',
        help_text='The user whom this application is for'
    )

    # Ethics Acknowledgement
    code_of_ethics_acknowledgement = models.BooleanField(
        verbose_name='Code of Ethics Acknowledgement',
        help_text='Applicant acknowledges code of ethics'
    )

    # Application Information
    application_type = models.CharField(
        max_length=20, blank=True, choices=(ApplicationChoices.choices),
        help_text='Type of application: New or Renewal'
    )
    position = models.CharField(
        max_length=20, blank=True, choices=(PositionChoices.choices),
        help_text='Position being applied for: SAPR VA or SARC / SAPR PM'
    )
    status = models.CharField(
        max_length=50, blank=True, choices=(StatusChoices.choices), default=(StatusChoices.DRAFT),
        help_text='Current status of the application'
    )
    policy = models.CharField(
        max_length=100, blank=True, default='dod-xxxx',
        help_text='Policy reference number'
    )
    application_version = models.IntegerField(
        default=1, blank=True,
        help_text='Version number of the application'
    )

    # Personal Information
    first_name = models.CharField(
        max_length=255, blank=True, validators=[
            RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
        ]
    )
    last_name = models.CharField(
        max_length=255, blank=True, validators=[
            RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
        ]
    )
    middle_initial = models.CharField(
        max_length=1, blank=True, validators=[
            RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
        ]
    )

    # Military/Affiliation Information
    affiliation = models.CharField(
        max_length=255, blank=True, validators=[
            RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
        ]
    )
    mili_status = models.CharField(
        max_length=100, blank=True, verbose_name='Military Status',
        validators=[
            RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
        ]
    )
    rank = models.CharField(
        max_length=50, blank=True, validators=[
            RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
        ]
    )
    grade = models.CharField(
        max_length=50, blank=True, validators=[
            RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
        ]
    )
    command_unit = models.CharField(
        max_length=255, blank=True, validators=[
            RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
        ]
    )
    installation = models.CharField(
        max_length=255, blank=True, validators=[
            RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
        ]
    )

    # Contact Information
    work_email = models.EmailField(blank=True)
    has_mil_gov_work_email = models.BooleanField(
        default=False, 
        help_text='Indicates if user has military/government work email'
    )
    other_sarc_email = models.EmailField(
        blank=True, verbose_name='Other Email'
    )
    dsn_code = models.CharField(
        max_length=20, blank=True, verbose_name='DSN Code',
        validators=[
            RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
        ]
    )
    work_phone = models.CharField(
        max_length=20, blank=True, validators=[
            RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
        ]
    )
    work_phone_ext = models.CharField(
        max_length=10, blank=True, verbose_name='Work Phone Extension',
        validators=[
            RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
        ]
    )

    # Certification Information

    # file class to be created later to hold certification_file

    certification_awarded_date = models.DateField(
        null=True, blank=True,
        help_text='Date when certification was awarded'
    )
    certification_expiration_date = models.DateField(
        null=True, blank=True,
        help_text='Date when certification expires'
    )
    no_experience_needed = models.BooleanField(
        default=False, blank=True,
        help_text='Check if no experience is needed for this application'
    )

    # Supervisor Information
    supervisor_last_name = models.CharField(
        max_length=255, blank=True, validators=[
            RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
        ]
    )
    supervisor_first_name = models.CharField(
        max_length=255, blank=True, validators=[
            RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
        ]
    )
    supervisor_email = models.EmailField(blank=True)

    # SARC Information
    sarc_last_name = models.CharField(
        max_length=255, blank=True, verbose_name='SARC Last Name',
        validators=[
            RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
        ]
    )
    sarc_first_name = models.CharField(
        max_length=255, blank=True, verbose_name='SARC First Name',
        validators=[
            RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
        ]
    )
    sarc_email = models.EmailField(blank=True, verbose_name='SARC Email')

    # Commanding Officer Information
    commanding_officer_last_name = models.CharField(
        max_length=255, blank=True, verbose_name='CO Last Name',
        validators=[
            RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
        ]
    )
    commanding_officer_first_name = models.CharField(
        max_length=255, blank=True, verbose_name='CO First Name',
        validators=[
            RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
        ]
    )
    commanding_officer_email = models.EmailField(
        blank=True, verbose_name='CO Email'
    )
    co_same_as_supervisor = models.BooleanField(
        default=False, verbose_name='CO same as Supervisor',
        help_text='Check if commanding officer is the same as supervisor'
    )

    # Submission Information
    final_submission = models.BooleanField(
        default=False, blank=True,
        help_text='Indicates the application has been submitted'
    )
    final_submission_stamp = models.DateTimeField(
        blank=True, null=True,
        help_text='Timestamp of final submission'
    )

    class Meta:
        verbose_name = 'Application'
        verbose_name_plural = 'Applications'

    def __str__(self):
        return f'{self.application_type} - {self.first_name} {self.last_name} ({self.status})'


class ApplicationComment(TimeStampedModel):
    """
    Comments/feedback on applications from reviewers.
    """
    application = models.ForeignKey(
        Application, on_delete=models.CASCADE, related_name='comments',
        help_text='The application this comment belongs to'
    )
    reviewer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='application_comments',
        help_text='The user who wrote this comment'
    )
    comment = models.TextField(
        blank=True,
        validators=[
            RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
        ],
        help_text='Comment text'
    )

    class Meta:
        verbose_name = 'Application Comment'
        verbose_name_plural = 'Application Comments'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.application.save(update_fields=['modified',])

    def __str__(self):
        return f'Comment by {self.reviewer} on Application {self.application.id}'


class ApplicationExperience(TimeStampedModel):
    """
    Work experience records associated with an application.
    """
    application = models.ForeignKey(
        Application, on_delete=models.CASCADE, related_name='experiences',
        help_text='The application this experience belongs to'
    )
    display_order = models.IntegerField(
        default=0,
        help_text='Order in which to display this experience'
    )
    position_name = models.CharField(
        max_length=255, validators=[
            RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
        ],
        help_text='Title/name of the position'
    )
    start_date = models.DateField(help_text='Start date of experience')
    end_date = models.DateField(
        blank=True, null=True,
        help_text='End date of experience (blank if ongoing)'
    )
    advocacy_hours = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00,
        help_text='Number of advocacy hours accumulated'
    )
    marked_for_evaluation = models.BooleanField(
        default=False,
        help_text='Flag indicating if this experience should be evaluated'
    )

    # Supervisor Information for this experience
    supervisor_last_name = models.CharField(
        max_length=255, blank=True, validators=[
            RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
        ]
    )
    supervisor_first_name = models.CharField(
        max_length=255, blank=True, validators=[
            RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
        ]
    )
    supervisor_email = models.EmailField(blank=True)
    supervisor_not_available = models.BooleanField(
        default=False, verbose_name='Supervisor Not Available',
        help_text='Check if supervisor is not available for verification'
    )

    # Proof/Documentation

    # file class later to hold to be created proof_file


    class Meta:
        verbose_name = 'Application Experience'
        verbose_name_plural = 'Application Experiences'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.application.save(update_fields=['modified',])

    def __str__(self):
        return f'{self.position_name} for Application {self.application.id}'


class ApplicationCourse(TimeStampedModel):
    """
    Training courses completed as part of an application.
    """
    application = models.ForeignKey(
        Application, on_delete=models.CASCADE, related_name='courses',
        help_text='The application this course belongs to'
    )
    display_order = models.IntegerField(
        default=0,
        help_text='Order in which to display this course'
    )
    category = models.CharField(
        max_length=255, blank=True,
        help_text='Category or competency area (e.g., competency)',
        validators=[
            RegexValidator(regex=REGEX_CHECK, message=REGEX_ERROR_MESSAGE),
        ]
    )
    xds_course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='application_courses', 
        null=True
    )
    completion_date = models.DateField(
        help_text='Date when the course was completed', blank=True
    )
    clocked_hours = models.DecimalField(
        max_digits=6, decimal_places=2, default=0.00, blank=True,
        help_text='Number of hours for this course'
    )

    # Return the name of the course
    @property
    def course_name(self):
        return self.xds_course.name

    class Meta:
        ordering = ['-completion_date']
        verbose_name = 'Application Course'
        verbose_name_plural = 'Application Courses'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.application.save(update_fields=['modified',])

    def __str__(self):
        return f'Course {self.xds_course_id or self.category} for Application {self.application.id}'
