# Seller Dashboard API Documentation

## Table of Contents
1. [Authentication](#authentication)
2. [Dashboard Statistics](#dashboard-statistics)
3. [Products Management](#products-management)
4. [Orders Management](#orders-management)
5. [Payments Tracking](#payments-tracking)
6. [Shipments Tracking](#shipments-tracking)
7. [Error Handling](#error-handling)
8. [Pagination](#pagination)

## Authentication

All endpoints require authentication using JWT (JSON Web Token).

**Login to get token:**
```http
POST /auth/login/
Content-Type: application/json

{
    "email": "seller@example.com",
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

Get overall statistics for the seller's store.

**Request:**
```http
GET /sellers/dashboard/seller/stats/
Authorization: Bearer your_jwt_token
```

**Response:**
```json
{
    "total_products": 25,
    "total_orders": 150,
    "total_revenue": "4599.97",
    "pending_orders": 10,
    "processing_orders": 5,
    "shipped_orders": 120,
    "delivered_orders": 100,
    "cancelled_orders": 15
}
```

## Products Management

### List Products with Statistics

Get all products with order statistics.

**Request:**
```http
GET /sellers/dashboard/seller/products/
Authorization: Bearer your_jwt_token
```

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Number of items per page (default: 10, max: 100)

**Response:**
```json
{
    "count": 25,
    "next": "http://api.example.com/sellers/dashboard/seller/products/?page=2",
    "previous": null,
    "results": [
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "title": "Organic Face Cream",
            "description": "Natural face cream with organic ingredients",
            "price": "29.99",
            "stock": 50,
            "category": "skincare",
            "total_orders": 25,
            "revenue": "749.75",
            "weight": "0.5",
            "length": "4.0",
            "width": "4.0",
            "height": "6.0",
            "free_shipping": false,
            "requires_shipping": true,
            "created_at": "2025-02-19T10:00:00Z",
            "updated_at": "2025-02-19T10:00:00Z"
        }
    ]
}
```

## Orders Management

### List Orders

Get all orders with filtering options.

**Request:**
```http
GET /sellers/dashboard/seller/orders/
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
    "count": 150,
    "next": "http://api.example.com/sellers/dashboard/seller/orders/?page=2",
    "previous": null,
    "results": [
        {
            "id": "9e57a287-2086-4270-99b6-a9d277dc46f7",
            "product": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "title": "Organic Face Cream",
                "price": "29.99"
            },
            "buyer_name": "John Doe",
            "buyer_email": "john@example.com",
            "quantity": 2,
            "total_price": "59.98",
            "status": "processing",
            "payment_status": "completed",
            "shipping_status": "PENDING",
            "tracking_number": "9405511234567890123456",
            "shipping_label_url": "https://shippo-delivery.s3.amazonaws.com/label_123.pdf",
            "created_at": "2025-02-19T15:00:00Z",
            "updated_at": "2025-02-19T15:01:00Z"
        }
    ]
}
```

### Update Order Status

Update the status of an order.

**Request:**
```http
POST /sellers/dashboard/seller/update_order_status/{order_id}/
Authorization: Bearer your_jwt_token
Content-Type: application/json

{
    "status": "shipped"
}
```

**Response:**
```json
{
    "id": "9e57a287-2086-4270-99b6-a9d277dc46f7",
    "status": "shipped",
    "updated_at": "2025-02-19T15:02:00Z"
}
```

## Payments Tracking

Get payment information for orders.

**Request:**
```http
GET /sellers/dashboard/seller/payments/?status=completed
Authorization: Bearer your_jwt_token
```

**Query Parameters:**
- `status`: pending, completed, failed

**Response:**
```json
{
    "count": 1,
    "results": [
        {
            "id": "7a1b5428-13c9-4d85-8c09-c88d1f6e34a2",
            "order": {
                "id": "9e57a287-2086-4270-99b6-a9d277dc46f7",
                "product": {
                    "title": "Organic Face Cream",
                    "price": "29.99"
                },
                "total_price": "59.98"
            },
            "amount": "59.98",
            "payment_status": "completed",
            "transaction_id": "tx_12345678",
            "created_at": "2025-02-19T15:03:00Z"
        }
    ]
}
```

## Shipments Tracking

Get shipping information for orders.

**Request:**
```http
GET /sellers/dashboard/seller/shipments/?status=TRANSIT
Authorization: Bearer your_jwt_token
```

**Query Parameters:**
- `status`: PENDING, TRANSIT, DELIVERED, RETURNED, FAILURE

**Response:**
```json
{
    "count": 1,
    "results": [
        {
            "id": "8b2c6539-24da-5e96-9d10-d99e2f7e45b3",
            "order": {
                "id": "9e57a287-2086-4270-99b6-a9d277dc46f7",
                "product": {
                    "title": "Organic Face Cream"
                }
            },
            "tracking_number": "9405511234567890123456",
            "tracking_url": "https://tools.usps.com/go/TrackConfirmAction?tLabels=9405511234567890123456",
            "label_url": "https://shippo-delivery.s3.amazonaws.com/label_123.pdf",
            "carrier": "USPS",
            "shipping_method": "Priority Mail",
            "shipping_cost": "12.99",
            "status": "TRANSIT",
            "created_at": "2025-02-19T15:00:00Z",
            "updated_at": "2025-02-19T15:01:00Z",
            "shipped_at": "2025-02-19T15:01:00Z",
            "delivered_at": null
        }
    ]
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
    "error": "Order not found"
}
```

#### 400 Bad Request
```json
{
    "error": "Invalid status. Must be one of [pending, processing, shipped, delivered, cancelled]"
}
```


## Rate Limiting
- API requests are limited to 100 requests per hour per user
- Rate limit headers are included in the response:
  ```
  X-RateLimit-Limit: 100
  X-RateLimit-Remaining: 95
  X-RateLimit-Reset: 1582149600
  ```

## Pagination

All list endpoints support pagination with the following query parameters:
- `page`: Page number (default: 1)
- `page_size`: Number of items per page (default: 10, max: 100)

**Example Request:**
```http
GET /sellers/dashboard/seller/products/?page=2&page_size=20
```

**Example Response:**
```json
{
    "count": 100,
    "next": "http://localhost:8000/sellers/dashboard/seller/products/?page=3&page_size=20",
    "previous": "http://localhost:8000/sellers/dashboard/seller/products/?page=1&page_size=20",
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