from django.urls import include, path
from rest_framework.routers import DefaultRouter

from vacancies import views

app_name = 'vacancies'

# Create a router and register our ViewSets with it.
router = DefaultRouter()
router.register(r'vacancy', views.VacancyViewSet,
                basename='vacancy')

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
]
