"""
URL configuration for portal project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, re_path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

urlpatterns = [
    re_path('admin/doc/', include('django.contrib.admindocs.urls')),
    re_path('admin/', admin.site.urls),
    re_path('api/', include('api.urls')),
    re_path('api/', include('configuration.urls')),
    re_path('api/', include('vacancies.urls')),
    re_path('api/', include('external.urls')),
    re_path('api/', include('graph.urls')),
    re_path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    re_path("api/schema/docs/",
            SpectacularSwaggerView.as_view(url_name="schema")),
    re_path('auth/', include('key_auth.urls')),
    re_path('health/', include('health_check.urls'),
            name='health_check')
]
