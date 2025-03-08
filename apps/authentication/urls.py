from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView, LoginView, LogoutView,
    VerifyEmailView, ResendVerificationView,
    ToggleUserActivationView, PasswordResetRequestView,
    PasswordResetConfirmView, UserListView, 
    SellerListView, UserDetailView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('verify-email/<uuid:token>/', VerifyEmailView.as_view(), name='verify-email'),
    path('resend-verification/', ResendVerificationView.as_view(), name='resend-verification'),
    path('toggle-activation/<uuid:user_id>/', ToggleUserActivationView.as_view(), name='toggle-activation'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('reset-password/<uuid:token>', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('reset-password/<uuid:token>/', PasswordResetConfirmView.as_view(), name='password-reset-confirm-slash'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/<uuid:id>/', UserDetailView.as_view(), name='user-detail'),
    path('sellers/', SellerListView.as_view(), name='seller-list'),
]
