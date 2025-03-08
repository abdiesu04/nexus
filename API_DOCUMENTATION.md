# AuraSpot Marketplace API Documentation

## Table of Contents
- [Authentication](#authentication)
- [Orders API](#orders-api)
- [Shipping API](#shipping-api)
- [Error Handling](#error-handling)

## Authentication

All endpoints require authentication using JWT (JSON Web Token).

**Header Format:**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

## Orders API

### 1. List Orders
Lists orders based on user role (buyers see their orders, sellers see orders for their products, admins see all orders).

**Endpoint**
```http
GET /orders/orders/
```

**Access Control**
- Buyers: View own orders
- Sellers: View orders for their products
- Admins: View all orders

**Response (200 OK)**
```json
{
    "count": 2,
    "results": [
        {
            "id": "9e57a287-2086-4270-99b6-a9d277dc46f7",
            "product": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "title": "Organic Face Cream"
            },
            "buyer": "user_id",
            "quantity": 2,
            "total_price": "59.98",
            "status": "pending",
            "created_at": "2025-02-19T15:00:00Z",
            "updated_at": "2025-02-19T15:00:00Z"
        }
    ]
}
```

### 2. Create Order
Creates a new order for a product.

**Endpoint**
```http
POST /orders/orders/
```

**Access Control**
- Buyers only

**Request Body**
```json
{
    "product": "550e8400-e29b-41d4-a716-446655440000",
    "quantity": 2
}
```

**Response (201 Created)**
```json
{
    "id": "9e57a287-2086-4270-99b6-a9d277dc46f7",
    "product": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "title": "Organic Face Cream"
    },
    "buyer": "user_id",
    "quantity": 2,
    "total_price": "59.98",
    "status": "pending",
    "created_at": "2025-02-19T15:00:00Z",
    "updated_at": "2025-02-19T15:00:00Z"
}
```

### 3. Get Order Details
Retrieves detailed information about a specific order.

**Endpoint**
```http
GET /orders/orders/{order_id}/
```

**Access Control**
- Buyers: View own orders
- Sellers: View orders for their products
- Admins: View any order

**Response (200 OK)**
```json
{
    "id": "9e57a287-2086-4270-99b6-a9d277dc46f7",
    "product": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "title": "Organic Face Cream"
    },
    "buyer": "user_id",
    "quantity": 2,
    "total_price": "59.98",
    "status": "pending",
    "created_at": "2025-02-19T15:00:00Z",
    "updated_at": "2025-02-19T15:00:00Z"
}
```

### 4. Update Order Status
Updates the status of an existing order.

**Endpoint**
```http
POST /orders/orders/{order_id}/update_status/
```

**Access Control**
- Sellers: Update status of their product orders
- Admins: Update any order status

**Request Body**
```json
{
    "status": "processing"
}
```

**Valid Status Values**
- pending
- processing
- shipped
- delivered
- cancelled

**Response (200 OK)**
```json
{
    "id": "9e57a287-2086-4270-99b6-a9d277dc46f7",
    "status": "processing",
    "updated_at": "2025-02-19T15:01:00Z"
}
```

### 5. Cancel Order
Cancels an existing order if it hasn't been shipped.

**Endpoint**
```http
POST /orders/orders/{order_id}/cancel/
```

**Access Control**
- Buyers: Cancel own orders
- Admins: Cancel any order

**Conditions**
- Order must be in 'pending' or 'processing' status
- Cannot cancel shipped or delivered orders

**Response (200 OK)**
```json
{
    "id": "9e57a287-2086-4270-99b6-a9d277dc46f7",
    "status": "cancelled",
    "updated_at": "2025-02-19T15:02:00Z"
}
```

### 6. Process Payment
Processes payment for an order.

**Endpoint**
```http
POST /orders/payments/
```

**Access Control**
- Buyers: Pay for own orders
- Admins: Process payments for any order

**Request Body**
```json
{
    "order": "9e57a287-2086-4270-99b6-a9d277dc46f7"
}
```

**Response (201 Created)**
```json
{
    "id": "7a1b5428-13c9-4d85-8c09-c88d1f6e34a2",
    "order": "9e57a287-2086-4270-99b6-a9d277dc46f7",
    "amount": "59.98",
    "payment_status": "completed",
    "transaction_id": "tx_12345678",
    "created_at": "2025-02-19T15:03:00Z"
}
```

## Shipping API

### 1. Mark Order as Shipped
Marks an order as shipped.

**Endpoint**
```http
POST /shipping/orders/{order_id}/mark-shipped/
```

**Access Control**
- Sellers: Mark their product orders as shipped
- Admins: Mark any order as shipped

**Conditions**
- Order must be in 'pending' or 'processing' status
- Payment must be completed

**Response (200 OK)**
```json
{
    "message": "Order marked as shipped successfully",
    "order_id": "9e57a287-2086-4270-99b6-a9d277dc46f7",
    "status": "shipped",
    "updated_at": "2025-02-19T16:00:00Z"
}
```

### 2. Track Order
Retrieves tracking information for an order.

**Endpoint**
```http
GET /shipping/orders/{order_id}/track/
```

**Access Control**
- Buyers: Track own orders
- Sellers: Track their product orders
- Admins: Track any order

**Response (200 OK)**
```json
{
    "order_id": "9e57a287-2086-4270-99b6-a9d277dc46f7",
    "status": "shipped",
    "product": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "title": "Organic Face Cream"
    },
    "timeline": [
        {
            "status": "Order Placed",
            "timestamp": "2025-02-19T15:00:00Z"
        },
        {
            "status": "Payment completed",
            "timestamp": "2025-02-19T15:03:00Z"
        },
        {
            "status": "Shipped",
            "timestamp": "2025-02-19T16:00:00Z"
        }
    ]
}
```

## Error Handling

### Common Error Responses

#### 400 Bad Request
```json
{
    "error": "Invalid status. Must be one of [pending, processing, shipped, delivered, cancelled]"
}
```

#### 401 Unauthorized
```json
{
    "detail": "Authentication credentials were not provided."
}
```

#### 403 Forbidden
```json
{
    "error": "You are not authorized to perform this action"
}
```

#### 404 Not Found
```json
{
    "error": "Order not found"
}
```

## Additional Notes

1. All timestamps are in ISO 8601 format with UTC timezone
2. All IDs are UUIDs
3. Prices are decimal strings with 2 decimal places
4. Order status transitions:
   - pending → processing → shipped → delivered
   - pending/processing → cancelled

---
*Last Updated: February 19, 2025* 