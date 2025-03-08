from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from .models import EmailVerificationToken

def send_verification_email(user):
    """Send verification email to user"""
    # Create or get verification token
    token, created = EmailVerificationToken.objects.get_or_create(user=user)
    if not created and not token.is_valid():
        # If token exists but expired, create new one
        token.delete()
        token = EmailVerificationToken.objects.create(user=user)

    verification_url = f"{settings.BASE_URL}/auth/verify-email/{token.token}"
    
    # Email content
    subject = 'Verify your AuraSpot Marketplace account'
    html_message = render_to_string('authentication/verification_email.html', {
        'user': user,
        'verification_url': verification_url
    })
    plain_message = f"""
    Hi {user.first_name},

    Please verify your email address by clicking the link below:
    {verification_url}

    This link will expire in 24 hours.

    If you didn't create an account, you can safely ignore this email.

    Best regards,
    AuraSpot Marketplace Team
    """
    
    # Send email
    send_mail(
        subject=subject,
        message=plain_message,
        html_message=html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
    
    return token

def send_password_reset_email(user):
    """Send password reset email to user"""
    # Create or get reset token
    token, created = EmailVerificationToken.objects.get_or_create(user=user)
    if not created and not token.is_valid():
        # If token exists but expired, create new one
        token.delete()
        token = EmailVerificationToken.objects.create(user=user)

    reset_url = f"{settings.BASE_URL}/auth/reset-password/{token.token}"
    
    # Email content
    subject = 'Reset your AuraSpot Marketplace password'
    html_message = render_to_string('authentication/password_reset_email.html', {
        'user': user,
        'reset_url': reset_url
    })
    plain_message = f"""
    Hi {user.first_name},

    We received a request to reset your password. Click the link below to set a new password:
    {reset_url}

    This link will expire in 24 hours.

    If you didn't request this password reset, you can safely ignore this email.

    Best regards,
    AuraSpot Marketplace Team
    """
    
    # Send email
    send_mail(
        subject=subject,
        message=plain_message,
        html_message=html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
    
    return token

def send_welcome_email(user):
    """Send welcome email to newly registered user"""
    subject = 'Welcome to AuraSpot Marketplace!'
    html_message = render_to_string('authentication/welcome_email.html', {
        'user': user,
        'base_url': settings.BASE_URL
    })
    plain_message = f"""
    Hi {user.first_name},

    Welcome to AuraSpot Marketplace! We're excited to have you as a {user.role}.

    To get started, please verify your email address using the verification link we sent in a separate email.

    If you have any questions or need assistance, our support team is here to help!

    Visit us at: {settings.BASE_URL}
    Contact Support: support@auraspot.com

    Best regards,
    The AuraSpot Marketplace Team
    """
    
    # Send email
    send_mail(
        subject=subject,
        message=plain_message,
        html_message=html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    ) 