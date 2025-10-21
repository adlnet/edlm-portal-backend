from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api import views

app_name = 'api'

# Create a router and register our ViewSets with it.
router = DefaultRouter()
router.register(r'profile-questions', views.ProfileQuestionViewSet,
                basename='profile-questions')
router.register(r'profile-responses', views.ProfileResponseViewSet,
                basename='profile-responses')
router.register('candidate-lists', views.CandidateListViewSet,
                basename='candidate-lists')
router.register('candidate-rankings', views.CandidateRankingViewSet,
                basename='candidate-rankings')
router.register('training-plans', views.TrainingPlanListViewSet,
                basename='training-plans')
router.register(r'learning-plans', views.LearningPlanViewSet,
                basename='learning-plans')
router.register(r'learning-plan-competencies',
                views.LearningPlanCompetencyViewSet,
                basename='learning-plan-competencies')
router.register(r'learning-plan-goals', views.LearningPlanGoalViewSet,
                basename='learning-plan-goals')
router.register(r'learning-plan-goal-ksas', views.LearningPlanGoalKsaViewSet,
                basename='learning-plan-goal-ksas')

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
    path('course-progress/', views.GetCourseProgressView.as_view(),
         name='course_progress'),
]
