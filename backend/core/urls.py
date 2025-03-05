"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.permissions import AllowAny

from users.views import UserViewSet, CustomTokenObtainPairView
from doctors.views import (
    SpecializationViewSet,
    DoctorProfileViewSet,
    DoctorDocumentViewSet,
    ReviewViewSet
)
from chat.views import ChatRoomViewSet, MessageViewSet, OnlineStatusViewSet

# Schema view for API documentation
schema_view = get_schema_view(
    openapi.Info(
        title="Healthcare API",
        default_version='v1',
        description="API for Healthcare Platform",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@healthcare.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[AllowAny],
)

# API Router
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'specializations', SpecializationViewSet)
router.register(r'doctors', DoctorProfileViewSet)
router.register(r'documents', DoctorDocumentViewSet, basename='documents')
router.register(r'reviews', ReviewViewSet, basename='reviews')
router.register(r'chat-rooms', ChatRoomViewSet, basename='chat-rooms')
router.register(r'messages', MessageViewSet, basename='messages')
router.register(r'online-status', OnlineStatusViewSet, basename='online-status')

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # Authentication endpoints
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # API endpoints
    path('api/', include(router.urls)),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
