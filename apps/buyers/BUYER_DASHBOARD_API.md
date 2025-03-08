# Buyer Dashboard API Documentation

## Table of Contents
1. [Authentication](#authentication)
2. [Dashboard Statistics](#dashboard-statistics)
3. [Order Management](#order-management)
4. [Wishlist Management](#wishlist-management)
5. [Error Handling](#error-handling)
6. [Pagination](#pagination)

## Authentication

All endpoints require authentication using JWT (JSON Web Token).

**Login to get token:**
```http
POST /auth/login/
Content-Type: application/json

{
    "email": "buyer@example.com",
    "password": "your_password"
}
```

**Response:**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1..."
}
```

Use the access token in subsequent requests:
```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1...
```

## Dashboard Statistics

Get overall statistics for the buyer's account.

**Request:**
```http
GET /buyers/dashboard/buyer/stats/
Authorization: Bearer your_jwt_token
```

**Response:**
```json
{
    "total_orders": 25,
    "active_orders": 3,
    "completed_orders": 20,
    "cancelled_orders": 2,
    "total_spent": "1299.97",
    "wishlist_count": 5
}
```

## Order Management

### List All Orders

Get complete order history with filtering options.

**Request:**
```http
GET /buyers/dashboard/buyer/orders/
Authorization: Bearer your_jwt_token
```

**Query Parameters:**
- `status`: Filter by status (pending, processing, shipped, delivered, cancelled)
- `date`: Filter by date range (today, week, month)
- `page`: Page number (default: 1)
- `page_size`: Number of items per page (default: 10, max: 100)

**Response:**
```json
{
    "count": 25,
    "next": "http://api.example.com/buyers/dashboard/buyer/orders/?page=2",
    "previous": null,
    "results": [
        {
            "id": "9e57a287-2086-4270-99b6-a9d277dc46f7",
            "product": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "title": "Organic Face Cream",
                "price": "29.99",
                "seller": "seller_id"
            },
            "quantity": 2,
            "total_price": "59.98",
            "status": "processing",
            "payment_status": "completed",
            "shipping_status": "PENDING",
            "tracking_number": "9405511234567890123456",
            "tracking_url": "https://tracking.example.com/9405511234567890123456",
            "estimated_delivery_date": "2025-02-25",
            "created_at": "2025-02-19T15:00:00Z",
            "updated_at": "2025-02-19T15:01:00Z"
        }
    ]
}
```

### List Active Orders

Get only active (pending, processing, shipped) orders.

**Request:**
```http
GET /buyers/dashboard/buyer/active_orders/
Authorization: Bearer your_jwt_token
```

**Response:**
```json
{
    "count": 3,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": "9e57a287-2086-4270-99b6-a9d277dc46f7",
            "product": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "title": "Organic Face Cream",
                "price": "29.99"
            },
            "status": "processing",
            "shipping_status": "PENDING",
            "estimated_delivery_date": "2025-02-25"
        }
    ]
}
```

## Wishlist Management

### Get Wishlist

Get all products in the wishlist.

**Request:**
```http
GET /buyers/dashboard/buyer/wishlist/
Authorization: Bearer your_jwt_token
```

**Response:**
```json
{
    "count": 5,
    "next": null,
    "previous": null,
    "results": [    
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "title": "Organic Face Cream",
            "description": "Natural face cream with organic ingredients",
            "price": "29.99",
            "stock": 50,
            "category": "skincare",
            "image": "https://example.com/images/face-cream.jpg",
            "created_at": "2025-02-19T10:00:00Z",
            "updated_at": "2025-02-19T10:00:00Z"
        }
    ]
}
```

### Add to Wishlist

Add a product to the wishlist.

**Request:**
```http
POST /buyers/dashboard/buyer/add_to_wishlist/{product_id}/
Authorization: Bearer your_jwt_token
```

**Response:**
```json
{
    "message": "Product added to wishlist"
}
```

### Remove from Wishlist

Remove a product from the wishlist.

**Request:**
```http
POST /buyers/dashboard/buyer/remove_from_wishlist/{product_id}/
Authorization: Bearer your_jwt_token
```

**Response:**
```json
{
    "message": "Product removed from wishlist"
}
```

## Error Handling

### Common Error Responses

#### 401 Unauthorized
```json
{
    "detail": "Authentication credentials were not provided."
}
```

#### 403 Forbidden
```json
{
    "detail": "You do not have permission to perform this action."
}
```

#### 404 Not Found
```json
{
    "error": "Product not found"
}
```

#### 400 Bad Request
```json
{
    "message": "Product already in wishlist"
}
```

## Pagination

All list endpoints support pagination with the following query parameters:
- `page`: Page number (default: 1)
- `page_size`: Number of items per page (default: 10, max: 100)

**Example Request:**
```http
GET /buyers/dashboard/buyer/orders/?page=2&page_size=20
```

**Example Response:**
```json
{
    "count": 100,
    "next": "http://localhost:8000/buyers/dashboard/buyer/orders/?page=3&page_size=20",
    "previous": "http://localhost:8000/buyers/dashboard/buyer/orders/?page=1&page_size=20",
    "results": [
        // Array of items
    ]
}
```

### Pagination Response Format
- `count`: Total number of items
- `next`: URL to fetch the next page (null if no more pages)
- `previous`: URL to fetch the previous page (null if on first page)
- `results`: Array of items for the current page

---
*Last Updated: February 21, 2025* 