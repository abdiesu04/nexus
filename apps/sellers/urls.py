from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SellerDashboardViewSet

router = DefaultRouter()
router.register(r'dashboard/seller', SellerDashboardViewSet, basename='seller-dashboard')

urlpatterns = [
    path('', include(router.urls)),
] 