from rest_framework import serializers
from .models import Specialization, DoctorProfile, DoctorDocument, Review
from users.serializers import UserSerializer

class SpecializationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialization
        fields = '__all__'

class DoctorDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorDocument
        fields = ('id', 'document_type', 'file', 'uploaded_at', 'verified', 'admin_notes')
        read_only_fields = ('verified', 'admin_notes')

class ReviewSerializer(serializers.ModelSerializer):
    patient = UserSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ('id', 'doctor', 'patient', 'rating', 'comment', 
                 'created_at', 'is_verified_consultation')
        read_only_fields = ('is_verified_consultation',)

class DoctorProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    specializations = SpecializationSerializer(many=True, read_only=True)
    documents = DoctorDocumentSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    specialization_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=Specialization.objects.all(),
        source='specializations'
    )

    class Meta:
        model = DoctorProfile
        fields = ('id', 'user', 'specializations', 'specialization_ids',
                 'years_of_experience', 'medical_license_number', 'education',
                 'bio', 'current_workplace', 'consultation_fee', 'languages',
                 'verification_status', 'average_rating', 'total_reviews',
                 'is_available', 'documents', 'reviews', 'created_at')
        read_only_fields = ('verification_status', 'average_rating', 
                          'total_reviews', 'created_at')

class DoctorProfileListSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    specializations = SpecializationSerializer(many=True, read_only=True)

    class Meta:
        model = DoctorProfile
        fields = ('id', 'user', 'specializations', 'years_of_experience',
                 'current_workplace', 'consultation_fee', 'average_rating',
                 'total_reviews', 'is_available')

class DoctorVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorProfile
        fields = ('verification_status',)
        read_only_fields = ('verification_status',) 