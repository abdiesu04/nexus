from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.

class Specialization(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.ImageField(upload_to='specialization_icons/', null=True, blank=True)

    def __str__(self):
        return self.name

class DoctorProfile(models.Model):
    class VerificationStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        UNDER_REVIEW = 'UNDER_REVIEW', 'Under Review'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='doctor_profile'
    )
    specializations = models.ManyToManyField(Specialization)
    years_of_experience = models.PositiveIntegerField(default=0)
    medical_license_number = models.CharField(max_length=50, unique=True)
    education = models.TextField()
    bio = models.TextField()
    current_workplace = models.CharField(max_length=200)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2)
    languages = models.JSONField(default=list)
    verification_status = models.CharField(
        max_length=20,
        choices=VerificationStatus.choices,
        default=VerificationStatus.PENDING
    )
    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0.00), MaxValueValidator(5.00)]
    )
    total_reviews = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Dr. {self.user.get_full_name()}"

class DoctorDocument(models.Model):
    class DocumentType(models.TextChoices):
        MEDICAL_LICENSE = 'MEDICAL_LICENSE', 'Medical License'
        EDUCATION_CERTIFICATE = 'EDUCATION_CERTIFICATE', 'Education Certificate'
        IDENTITY_PROOF = 'IDENTITY_PROOF', 'Identity Proof'
        OTHER = 'OTHER', 'Other'

    doctor = models.ForeignKey(
        DoctorProfile,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    document_type = models.CharField(max_length=50, choices=DocumentType.choices)
    file = models.FileField(upload_to='doctor_documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False)
    admin_notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.doctor} - {self.document_type}"

class Review(models.Model):
    doctor = models.ForeignKey(
        DoctorProfile,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews_given'
    )
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_verified_consultation = models.BooleanField(default=False)

    class Meta:
        unique_together = ['doctor', 'patient']

    def __str__(self):
        return f"Review for {self.doctor} by {self.patient}"
