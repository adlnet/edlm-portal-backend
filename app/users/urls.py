from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()

app_name = 'users'
urlpatterns = [
    path('auth/validate', views.IsLoggedInView.as_view(), name='validate'),
]
