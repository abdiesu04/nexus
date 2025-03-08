# Authentication API Documentation

## Table of Contents
1. [Overview](#overview)
2. [Project Structure](#project-structure)
3. [API Endpoints](#api-endpoints)
4. [Models](#models)
5. [Email Verification](#email-verification)
6. [Error Handling](#error-handling)
7. [Configuration](#configuration)

## Overview

The Authentication API provides user management functionality including registration, login, logout, and email verification. It uses JWT (JSON Web Token) for authentication and includes role-based access control.

### Features
- User registration with email verification
- JWT-based authentication
- Role-based access (Admin, Seller, Buyer)
- Email verification system
- Token refresh mechanism
- Secure logout with token blacklisting

## Project Structure

```
apps/authentication/
├── migrations/              # Database migrations
├── templates/              
│   └── authentication/     
│       └── verification_email.html  # Email template
├── __init__.py
├── admin.py                # Admin configuration
├── apps.py                 # App configuration
├── models.py               # Data models
├── serializers.py         # API serializers
├── urls.py                # URL routing
├── utils.py               # Utility functions
└── views.py               # API views
```

## API Endpoints

### 1. Register User
Creates a new user account and sends verification email.

**Endpoint:** `POST /auth/register/`

**Request Body:**
```json
{
    "email": "user@example.com",
    "username": "username",
    "password": "secure_password123",
    "confirm_password": "secure_password123",
    "first_name": "John",
    "last_name": "Doe",
    "role": "buyer"
}
```

**Required Fields:**
- `email`: Valid email address (unique)
- `username`: Username (unique)
- `password`: Password (min 8 characters)
- `confirm_password`: Must match password
- `first_name`: First name
- `last_name`: Last name
- `role`: One of ["buyer", "seller", "admin"]

**Response (201 Created):**
```json
{
    "user": {
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "role": "buyer",
        "is_verified": false
    },
    "message": "Please check your email to verify your account"
}
```

### 2. Login
Authenticates a user and returns JWT tokens.

**Endpoint:** `POST /auth/login/`

**Request Body:**
```json
{
    "email": "user@example.com",
    "password": "secure_password123"
}
```

**Response (200 OK):**
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1...",
    "user": {
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "role": "buyer",
        "is_verified": true
    }
}
```

### 3. Verify Email
Verifies user's email address using the token sent via email.

**Endpoint:** `GET /auth/verify-email/{token}/`

**Response (200 OK):**
```json
{
    "message": "Email verified successfully",
    "user": {
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "role": "buyer",
        "is_verified": true
    }
}
```

### 4. Resend Verification Email
Resends the verification email if the original expired or was lost.

**Endpoint:** `POST /auth/resend-verification/`

**Request Body:**
```json
{
    "email": "user@example.com"
}
```

**Response (200 OK):**
```json
{
    "message": "Verification email sent successfully"
}
```

### 5. Logout
Logs out the user by blacklisting the refresh token.

**Endpoint:** `POST /auth/logout/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1..."
}
```

**Response (200 OK):**
```json
{
    "message": "Logged out successfully"
}
```

### 6. Refresh Token
Gets a new access token using refresh token.

**Endpoint:** `POST /auth/token/refresh/`

**Request Body:**
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1..."
}
```

**Response (200 OK):**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1..."
}
```

### 7. Toggle User Activation (Admin Only)
Allows administrators to activate or deactivate user accounts.

**Endpoint:** `POST /auth/toggle-activation/{user_id}/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Permissions:**
- Must be authenticated
- Must have admin role

**Response (200 OK):**
```json
{
    "message": "User account activated successfully",
    "user": {
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "role": "buyer",
        "is_verified": true,
        "is_active": true
    }
}
```

**Error Responses:**

401 Unauthorized:
```json
{
    "detail": "Authentication credentials were not provided."
}
```

403 Forbidden:
```json
{
    "detail": "You do not have permission to perform this action."
}
```

404 Not Found:
```json
{
    "error": "User not found"
}
```

### 8. Request Password Reset
Sends a password reset email to the user.

**Endpoint:** `POST /auth/password-reset/`

**Request Body:**
```json
{
    "email": "user@example.com"
}
```

**Response (200 OK):**
```json
{
    "message": "Password reset email sent successfully"
}
```

### 9. Reset Password
Resets the user's password using the token from the email.

**Endpoint:** `POST /auth/reset-password/{token}/`

**Request Body:**
```json
{
    "password": "newSecurePass123",
    "confirm_password": "newSecurePass123"
}
```

**Response (200 OK):**
```json
{
    "message": "Password reset successful"
}
```

**Error Responses:**

400 Bad Request (Invalid Token):
```json
{
    "error": "Password reset link has expired. Please request a new one."
}
```

400 Bad Request (Passwords Don't Match):
```json
{
    "confirm_password": "Passwords do not match."
}
```

400 Bad Request (Password Too Short):
```json
{
    "password": "Ensure this field has at least 8 characters."
}
```

### 10. List All Users (Admin Only)
Lists all users with pagination and filtering options.

**Endpoint:** `GET /auth/users/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Number of items per page (default: 10, max: 100)
- `role`: Filter by role ("admin", "seller", "buyer")
- `search`: Search in username, email, first name, last name

**Response (200 OK):**
```json
{
    "count": 100,
    "next": "http://localhost:8000/auth/users/?page=2",
    "previous": null,
    "results": [
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "username": "johndoe",
            "full_name": "John Doe",
            "email": "john@example.com",
            "role": "seller",
            "is_verified": true,
            "is_active": true,
            "date_joined": "2025-03-04T10:00:00Z"
        },
        // ... more users
    ]
}
```

**Error Responses:**

401 Unauthorized:
```json
{
    "detail": "Authentication credentials were not provided."
}
```

403 Forbidden:
```json
{
    "detail": "You do not have permission to perform this action."
}
```

### 11. Get User Details (Admin Only)
Retrieves detailed information about a specific user.

**Endpoint:** `GET /auth/users/{user_id}/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "username": "johndoe",
    "full_name": "John Doe",
    "email": "john@example.com",
    "role": "seller",
    "is_verified": true,
    "is_active": true,
    "date_joined": "2025-03-04T10:00:00Z"
}
```

**Error Responses:**

401 Unauthorized:
```json
{
    "detail": "Authentication credentials were not provided."
}
```

403 Forbidden:
```json
{
    "detail": "You do not have permission to perform this action."
}
```

404 Not Found:
```json
{
    "detail": "Not found."
}
```

### 12. List All Sellers
Lists all sellers with pagination and search functionality.

**Endpoint:** `GET /auth/sellers/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Number of items per page (default: 10, max: 100)
- `search`: Search in username, email, first name, last name

**Response (200 OK):**
```json
{
    "count": 50,
    "next": "http://localhost:8000/auth/sellers/?page=2",
    "previous": null,
    "results": [
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "username": "seller1",
            "full_name": "John Seller",
            "email": "seller1@example.com",
            "role": "seller",
            "is_verified": true,
            "is_active": true,
            "date_joined": "2025-03-04T10:00:00Z"
        },
        // ... more sellers
    ]
}
```

**Error Responses:**

401 Unauthorized:
```json
{
    "detail": "Authentication credentials were not provided."
}
```

## Testing User Management Endpoints

### 1. List All Users (Admin)
```bash
curl -X GET http://localhost:8000/auth/users/ \
  -H "Authorization: Bearer your_admin_access_token" \
  -H "Content-Type: application/json"
```

### 2. Search Users by Role
```bash
curl -X GET "http://localhost:8000/auth/users/?role=seller&search=john" \
  -H "Authorization: Bearer your_admin_access_token" \
  -H "Content-Type: application/json"
```

### 3. Get User Details
```bash
curl -X GET http://localhost:8000/auth/users/123e4567-e89b-12d3-a456-426614174000/ \
  -H "Authorization: Bearer your_admin_access_token" \
  -H "Content-Type: application/json"
```

### 4. List Sellers
```bash
curl -X GET "http://localhost:8000/auth/sellers/?search=john" \
  -H "Authorization: Bearer your_access_token" \
  -H "Content-Type: application/json"
```

## Permissions Summary

| Endpoint | Method | Required Role | Description |
|----------|---------|---------------|-------------|
| `/auth/users/` | GET | Admin | List all users with filtering |
| `/auth/users/{id}/` | GET | Admin | Get user details |
| `/auth/sellers/` | GET | Authenticated | List all sellers |

## Query Parameters

### User List Endpoint
- `page`: Page number for pagination
- `page_size`: Number of items per page (10-100)
- `role`: Filter users by role (admin/seller/buyer)
- `search`: Search in user fields

### Seller List Endpoint
- `page`: Page number for pagination
- `page_size`: Number of items per page (10-100)
- `search`: Search in seller fields

## Response Format

All list endpoints return paginated responses in the following format:
```json
{
    "count": <total_items>,
    "next": <next_page_url>,
    "previous": <previous_page_url>,
    "results": [
        {
            "id": <uuid>,
            "username": <string>,
            "full_name": <string>,
            "email": <string>,
            "role": <string>,
            "is_verified": <boolean>,
            "is_active": <boolean>,
            "date_joined": <datetime>
        },
        // ... more items
    ]
}
```

## Models

### User Model
```python
class User(AbstractUser):
    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("seller", "Seller"),
        ("buyer", "Buyer"),
    )
    id = UUIDField(primary_key=True)
    first_name = CharField(max_length=255)
    last_name = CharField(max_length=255)
    email = EmailField(unique=True)
    role = CharField(max_length=10, choices=ROLE_CHOICES)
    is_verified = BooleanField(default=False)
    is_active = BooleanField(default=True)
```

### EmailVerificationToken Model
```python
class EmailVerificationToken(models.Model):
    user = OneToOneField(User, on_delete=CASCADE)
    token = UUIDField(default=uuid4)
    created_at = DateTimeField(auto_now_add=True)
    expires_at = DateTimeField()  # 24 hours from creation
```

## Email Verification

The system uses SMTP to send verification emails. When a user registers:
1. A verification token is created
2. An email is sent with the verification link
3. The token expires after 24 hours
4. Users can request a new verification email if needed

### Email Template
Located at `templates/authentication/verification_email.html`
- Includes both HTML and plain text versions
- Contains verification link with token
- Styled for better user experience

## Error Handling

### Common Error Responses

#### 400 Bad Request
```json
{
    "email": ["User with this email already exists."],
    "password": ["Passwords must match"]
}
```

#### 401 Unauthorized
```json
{
    "detail": "Invalid credentials"
}
```

#### 403 Forbidden
```json
{
    "error": "This account is inactive"
}
```

#### 404 Not Found
```json
{
    "error": "No user found with this email"
}
```

## Configuration

### Environment Variables
Required environment variables in `.env`:
```env
# JWT Configuration
JWT_SECRET_KEY=your_jwt_secret_key

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_FROM=your_email@gmail.com

# Base URL
BASE_URL=http://localhost:8000
```

### JWT Settings
```python
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=20),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": os.getenv("JWT_SECRET_KEY"),
    "AUTH_HEADER_TYPES": ("Bearer",),
}
```

### Email Settings
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('SMTP_HOST')
EMAIL_PORT = os.getenv('SMTP_PORT')
EMAIL_HOST_USER = os.getenv('SMTP_USERNAME')
EMAIL_HOST_PASSWORD = os.getenv('SMTP_PASSWORD')
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = os.getenv('SMTP_FROM')
```

## Testing the API

### 1. Register a New User
```bash
curl -X POST http://localhost:8000/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "securepass123",
    "confirm_password": "securepass123",
    "first_name": "Test",
    "last_name": "User",
    "role": "buyer"
  }'
```

### 2. Verify Email
Check email and click the verification link, or use:
```bash
curl -X GET http://localhost:8000/auth/verify-email/{token}/
```

### 3. Login
```bash
curl -X POST http://localhost:8000/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "securepass123"
  }'
```

### 4. Use Protected Endpoints
```bash
curl -X GET http://localhost:8000/protected-endpoint/ \
  -H "Authorization: Bearer your_access_token"
```

### 5. Toggle User Activation (Admin Only)
```bash
curl -X POST http://localhost:8000/auth/toggle-activation/{user_id}/ \
  -H "Authorization: Bearer admin_access_token"
```

### 6. Request Password Reset
```bash
curl -X POST http://localhost:8000/auth/password-reset/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'
```

### 7. Reset Password
```bash
curl -X POST http://localhost:8000/auth/reset-password/{token}/ \
  -H "Content-Type: application/json" \
  -d '{
    "password": "newSecurePass123",
    "confirm_password": "newSecurePass123"
  }'
```

### 8. List All Users (Admin)
```bash
curl -X GET http://localhost:8000/auth/users/ \
  -H "Authorization: Bearer your_admin_access_token" \
  -H "Content-Type: application/json"
```

### 9. Search Users by Role
```bash
curl -X GET "http://localhost:8000/auth/users/?role=seller&search=john" \
  -H "Authorization: Bearer your_admin_access_token" \
  -H "Content-Type: application/json"
```

### 10. Get User Details
```bash
curl -X GET http://localhost:8000/auth/users/123e4567-e89b-12d3-a456-426614174000/ \
  -H "Authorization: Bearer your_admin_access_token" \
  -H "Content-Type: application/json"
```

### 11. List Sellers
```bash
curl -X GET "http://localhost:8000/auth/sellers/?search=john" \
  -H "Authorization: Bearer your_access_token" \
  -H "Content-Type: application/json"
```

## Email Communication

### Registration Emails
When a user registers, they receive two emails:

1. **Welcome Email**
   - Personalized greeting
   - Role-specific getting started guide
   - Quick links to important features
   - Support contact information

2. **Verification Email**
   - Contains email verification link
   - Link expires after 24 hours
   - Can be resent if expired

Both emails use HTML templates with fallback plain text versions for better compatibility.

### Email Templates
Located in `templates/authentication/`:
- `welcome_email.html`: Welcome message and onboarding information
- `verification_email.html`: Email verification link
- `password_reset_email.html`: Password reset link

### Template Context
Welcome Email Template receives:
```python
{
    'user': {
        'first_name': str,
        'role': str,
        'email': str
    },
    'base_url': str  # Base URL of the application
}
```

---
*Last Updated: February 27, 2025* 