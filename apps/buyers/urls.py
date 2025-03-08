from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BuyerDashboardViewSet

router = DefaultRouter()
router.register(r'dashboard/buyer', BuyerDashboardViewSet, basename='buyer-dashboard')

urlpatterns = [
    path('', include(router.urls)),
] 