from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register viewsets
router = DefaultRouter()
router.register(r'seller-addresses', views.SellerAddressViewSet, basename='seller-address')
router.register(r'buyer-addresses', views.BuyerAddressViewSet, basename='buyer-address')

urlpatterns = [
    # Include the router URLs
    path('', include(router.urls)),
    
    # Shipping operations
    path('calculate-rates/', views.calculate_shipping_rates, name='calculate-shipping-rates'),
    path('labels/<uuid:shipping_id>/create/', views.create_shipping_label, name='create-shipping-label'),
    path('shipments/<uuid:shipping_id>/track/', views.track_shipment, name='track-shipment'),
] 