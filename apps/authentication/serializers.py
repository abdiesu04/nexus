from rest_framework import serializers
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
import re
from .models import User

class UserSerializer(serializers.ModelSerializer):
    """Serializer for user registration and details."""
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "role", "is_verified", "is_active"]

class UserListSerializer(serializers.ModelSerializer):
    """Serializer for listing users with additional fields."""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ["id", "username", "full_name", "email", "role", "is_verified", "is_active", "date_joined"]
        
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "username", "password", "confirm_password", "role", "is_verified", "is_active"]

    def validate_password(self, value):
        """Validate password strength."""
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")
            
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter.")
            
        if not re.search(r'[0-9]', value):
            raise serializers.ValidationError("Password must contain at least one number.")
            
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise serializers.ValidationError("Password must contain at least one special character.")
            
        try:
            # Use Django's built-in password validation
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
            
        return value

    def validate(self, data):
        """Ensure passwords match and validate user data."""
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "Passwords must match."})
            
        # Check if password contains personal information
        personal_info = [
            data.get('first_name', '').lower(),
            data.get('last_name', '').lower(),
            data.get('email', '').lower().split('@')[0],
            data.get('username', '').lower()
        ]
        
        password = data["password"].lower()
        for info in personal_info:
            if info and len(info) > 2 and info in password:
                raise serializers.ValidationError({
                    "password": "Password cannot contain your personal information (name, email, or username)."
                })
                
        return data

    def create(self, validated_data):
        validated_data.pop("confirm_password")  # Remove confirm_password before saving
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        """Validate the data without performing authentication"""
        if not data.get('email'):
            raise serializers.ValidationError({'email': 'Email is required'})
        if not data.get('password'):
            raise serializers.ValidationError({'password': 'Password is required'})
        return data

class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for requesting a password reset"""
    email = serializers.EmailField()

class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for confirming a password reset"""
    password = serializers.CharField(
        min_length=8,
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    confirm_password = serializers.CharField(
        min_length=8,
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    def validate_password(self, value):
        """Validate password strength."""
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")
            
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter.")
            
        if not re.search(r'[0-9]', value):
            raise serializers.ValidationError("Password must contain at least one number.")
            
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise serializers.ValidationError("Password must contain at least one special character.")
            
        try:
            # Use Django's built-in password validation
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
            
        return value

    def validate(self, data):
        """Validate that passwords match"""
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({
                'confirm_password': 'Passwords do not match.'
            })
        return data
