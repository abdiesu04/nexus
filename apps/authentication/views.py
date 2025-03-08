from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser, BasePermission
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import User, EmailVerificationToken
from .serializers import (
    UserSerializer, RegisterSerializer, LoginSerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer,
    UserListSerializer
)
from .utils import send_verification_email, send_password_reset_email, send_welcome_email
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from django.contrib.auth import authenticate

class IsAdminRole(BasePermission):
    """
    Custom permission to only allow users with admin role.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'admin'

class RegisterView(generics.CreateAPIView):
    """User Registration API"""
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    
    def perform_create(self, serializer):
        user = serializer.save()
        # Send verification email
        send_verification_email(user)
        # Send welcome email
        send_welcome_email(user)

class VerifyEmailView(APIView):
    """Email verification endpoint"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, token):
        # Get token object
        verification_token = get_object_or_404(EmailVerificationToken, token=token)
        
        # Check if token is valid
        if not verification_token.is_valid():
            verification_token.delete()
            return Response(
                {'error': 'Verification link has expired. Please request a new one.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify user
        user = verification_token.user
        user.is_verified = True
        user.save()
        
        # Delete used token
        verification_token.delete()
        
        return Response({
            'message': 'Email verified successfully',
            'user': UserSerializer(user).data
        })

class ResendVerificationView(APIView):
    """Resend verification email"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response(
                {'error': 'Email is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(email=email)
            if user.is_verified:
                return Response(
                    {'message': 'Email is already verified'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Send new verification email
            send_verification_email(user)
            return Response({
                'message': 'Verification email sent successfully'
            })
            
        except User.DoesNotExist:
            return Response(
                {'error': 'No user found with this email'},
                status=status.HTTP_404_NOT_FOUND
            )

class LoginView(APIView):
    """User Login API"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = User.objects.get(email=serializer.validated_data['email'])
            
            # Check if account is active
            if not user.is_active:
                return Response(
                    {"error": "This account has been deactivated. Please contact support."}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Check if email is verified
            if not user.is_verified:
                return Response(
                    {"error": "Please verify your email before logging in."}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Authenticate user
            authenticated_user = authenticate(
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password']
            )
            
            if not authenticated_user:
                return Response(
                    {"error": "Invalid password. Please try again."}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )

            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
            })
            
        except User.DoesNotExist:
            return Response(
                {"error": "No account found with this email address."}, 
                status=status.HTTP_404_NOT_FOUND
            )

class LogoutView(APIView):
    """Handles user logout by blacklisting refresh tokens."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()  # Blacklist the refresh token
            return Response({"message": "Logged out successfully"}, status=200)
        except Exception as e:
            return Response({"error": "Invalid token"}, status=400)

class ToggleUserActivationView(APIView):
    """Toggle user account activation status (Admin only)"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, user_id):
        if request.user.role != "admin":
            return Response(
                {"error": "Only admin users can perform this action"},
                status=status.HTTP_403_FORBIDDEN
            )
            
        try:
            user = User.objects.get(id=user_id)
            user.is_active = not user.is_active
            user.save()
            
            return Response({
                'message': f'User account {"activated" if user.is_active else "deactivated"} successfully',
                'user': UserSerializer(user).data
            })
            
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )

class PasswordResetRequestView(APIView):
    """Request password reset email"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            user = User.objects.get(email=serializer.validated_data['email'])
            token = send_password_reset_email(user)
            return Response({
                'message': 'Password reset email sent successfully'
            })
        except User.DoesNotExist:
            # Return success even if email doesn't exist for security
            return Response({
                'message': 'Password reset email sent successfully'
            })

class PasswordResetConfirmView(APIView):
    """Reset password with token"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, token):
        # Validate token
        try:
            reset_token = EmailVerificationToken.objects.get(token=token)
            if not reset_token.is_valid():
                reset_token.delete()
                return Response(
                    {'error': 'Password reset link has expired. Please request a new one.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except EmailVerificationToken.DoesNotExist:
            return Response(
                {'error': 'Invalid password reset token'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate new password
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Update password
        user = reset_token.user
        user.set_password(serializer.validated_data['password'])
        user.save()
        
        # Delete used token
        reset_token.delete()
        
        return Response({
            'message': 'Password reset successful'
        })

class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination class for consistent pagination across views."""
    page_size = 10  # Default number of items per page
    page_size_query_param = 'page_size'  # Allow client to override page size
    max_page_size = 100  # Maximum limit per page
    page_query_param = 'page'  # Parameter name for page number
    
    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,  # Total number of items
            'next': self.get_next_link(),  # URL for next page
            'previous': self.get_previous_link(),  # URL for previous page
            'results': data  # Page of results
        })

class UserListView(ListAPIView):
    """
    View to list all users with pagination.
    Only accessible by users with admin role.
    """
    serializer_class = UserListSerializer
    permission_classes = [IsAuthenticated, IsAdminRole]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = User.objects.all().order_by('-date_joined')
        role = self.request.query_params.get('role', None)
        search = self.request.query_params.get('search', None)
        
        if role:
            queryset = queryset.filter(role=role)
            
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )
            
        return queryset

class SellerListView(ListAPIView):
    """
    View to list all sellers with pagination.
    Accessible by authenticated users.
    """
    serializer_class = UserListSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = User.objects.filter(role='seller').order_by('-date_joined')
        search = self.request.query_params.get('search', None)
        
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )
            
        return queryset

class UserDetailView(RetrieveAPIView):
    """
    View to retrieve a user by ID.
    Only accessible by users with admin role.
    """
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [IsAuthenticated, IsAdminRole]
    lookup_field = 'id'
