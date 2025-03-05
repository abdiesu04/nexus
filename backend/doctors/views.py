from django.shortcuts import render
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from .models import Specialization, DoctorProfile, DoctorDocument, Review
from .serializers import (
    SpecializationSerializer,
    DoctorProfileSerializer,
    DoctorProfileListSerializer,
    DoctorDocumentSerializer,
    ReviewSerializer,
    DoctorVerificationSerializer
)

# Create your views here.

class SpecializationViewSet(viewsets.ModelViewSet):
    queryset = Specialization.objects.all()
    serializer_class = SpecializationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]

class DoctorProfileViewSet(viewsets.ModelViewSet):
    queryset = DoctorProfile.objects.all()
    serializer_class = DoctorProfileSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['specializations', 'verification_status', 'is_available']
    search_fields = ['user__first_name', 'user__last_name', 'bio', 'current_workplace']
    ordering_fields = ['average_rating', 'consultation_fee', 'years_of_experience']

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == 'list':
            return queryset.filter(verification_status='APPROVED')
        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return DoctorProfileListSerializer
        return DoctorProfileSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        if not request.user.is_staff:
            return Response(
                {"detail": "Not authorized"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        doctor = self.get_object()
        status_update = request.data.get('verification_status')
        if status_update in ['APPROVED', 'REJECTED']:
            doctor.verification_status = status_update
            doctor.save()
            return Response(
                DoctorVerificationSerializer(doctor).data
            )
        return Response(
            {"detail": "Invalid status"}, 
            status=status.HTTP_400_BAD_REQUEST
        )

class DoctorDocumentViewSet(viewsets.ModelViewSet):
    serializer_class = DoctorDocumentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return DoctorDocument.objects.filter(doctor__user=self.request.user)

    def perform_create(self, serializer):
        doctor_profile = DoctorProfile.objects.get(user=self.request.user)
        serializer.save(doctor=doctor_profile)

class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Review.objects.all()

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)

    def create(self, request, *args, **kwargs):
        # Check if user is a patient
        if request.user.user_type != 'PATIENT':
            return Response(
                {"detail": "Only patients can create reviews"},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().create(request, *args, **kwargs)
