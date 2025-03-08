# Shipping Documentation

## Table of Contents
1. [Overview](#overview)
2. [Shipping Flow](#shipping-flow)
3. [API Endpoints](#api-endpoints)
4. [Address Management](#address-management)
5. [Rate Calculation](#rate-calculation)
6. [Label Generation](#label-generation)
7. [Status Tracking](#status-tracking)
8. [Error Handling](#error-handling)

## Overview

The shipping system integrates with Shippo to provide real-time shipping rates, label generation, and tracking capabilities. It supports multiple carriers (USPS, UPS, FedEx) and various service levels.

## Shipping Flow

### 1. Order Creation
1. Buyer selects product and quantity
2. System checks shipping availability
3. Buyer selects shipping method
4. Payment is processed
5. Seller generates shipping label
6. Package is shipped and tracked

### 2. Cost Flow
- Buyer pays: Product price + Estimated shipping
- Seller receives: Product price
- Marketplace pays: Actual shipping cost to Shippo
- Adjustments: Handled by marketplace

## API Endpoints

### 1. Calculate Shipping Rates

**Endpoint:** `POST /shipping/calculate-rates/`

**Request:**
```json
{
    "order_id": "550e8400-e29b-41d4-a716-446655440000",
    "from_address_id": "123e4567-e89b-12d3-a456-426614174000",
    "to_address_id": "987fcdeb-51d3-12d3-a456-426614174000"
}
```

**Response:**
```json
{
    "shipping_id": "789e4567-e89b-12d3-a456-426614174000",
    "rates": [
        {
            "provider": "USPS",
            "service": "Priority Mail",
            "amount": "12.99",
            "currency": "USD",
            "duration_terms": "1-3 Business Days",
            "rate_id": "rate_123xyz",
            "estimated_days": 2
        },
        {
            "provider": "UPS",
            "service": "Ground",
            "amount": "15.99",
            "currency": "USD",
            "duration_terms": "3-5 Business Days",
            "rate_id": "rate_456abc",
            "estimated_days": 4
        }
    ]
}
```

### 2. Create Shipping Label

**Endpoint:** `POST /shipping/labels/{shipping_id}/create/`

**Request:**
```json
{
    "rate_id": "rate_123xyz"
}
```

**Response:**
```json
{
    "message": "Shipping label created successfully",
    "shipping_id": "789e4567-e89b-12d3-a456-426614174000",
    "tracking_number": "9405511234567890123456",
    "tracking_url": "https://tools.usps.com/go/TrackConfirmAction?tLabels=9405511234567890123456",
    "label_url": "https://shippo-delivery.s3.amazonaws.com/label_123.pdf",
    "rate_details": {
        "carrier": "USPS",
        "method": "Priority Mail",
        "cost": "12.99"
    }
}
```

### 3. Track Shipment

**Endpoint:** `GET /shipping/shipments/{shipping_id}/track/`

**Response:**
```json
{
    "tracking_number": "9405511234567890123456",
    "status": "TRANSIT",
    "status_details": "Package in transit",
    "status_date": "2025-02-20T15:00:00Z",
    "eta": "2025-02-22T15:00:00Z",
    "tracking_history": [
        {
            "status": "PENDING",
            "status_details": "Label created",
            "status_date": "2025-02-19T10:00:00Z"
        },
        {
            "status": "TRANSIT",
            "status_details": "Package in transit",
            "status_date": "2025-02-20T15:00:00Z"
        }
    ]
}
```

## Address Management

### 1. Add Buyer Address

**Endpoint:** `POST /shipping/buyer-addresses/`

**Request:**
```json
{
    "name": "John Doe",
    "street1": "123 Main Street",
    "city": "Los Angeles",
    "state": "CA",
    "zip_code": "90012",
    "country": "US",
    "phone": "1234567890",
    "email": "john@example.com",
    "is_residential": true
}
```

**Response:**
```json
{
    "id": "987fcdeb-51d3-12d3-a456-426614174000",
    "name": "John Doe",
    "street1": "123 Main Street",
    "city": "Los Angeles",
    "state": "California",
    "zip_code": "90012",
    "country": "US",
    "phone": "1234567890",
    "email": "john@example.com",
    "is_residential": true,
    "is_verified": true,
    "created_at": "2025-02-19T10:00:00Z"
}
```

### 2. Add Seller Address

**Endpoint:** `POST /shipping/seller-addresses/`

**Request:**
```json
{
    "name": "Business Name",
    "company": "Company Inc",
    "street1": "456 Market Street",
    "city": "San Francisco",
    "state": "CA",
    "zip_code": "94105",
    "country": "US",
    "phone": "1234567890",
    "email": "business@example.com",
    "is_warehouse": true
}
```

**Response:**
```json
{
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "name": "Business Name",
    "company": "Company Inc",
    "street1": "456 Market Street",
    "city": "San Francisco",
    "state": "California",
    "zip_code": "94105",
    "country": "US",
    "phone": "1234567890",
    "email": "business@example.com",
    "is_warehouse": true,
    "is_verified": true,
    "created_at": "2025-02-19T10:00:00Z"
}
```

## Rate Calculation

Shipping rates are calculated based on:
- Package dimensions and weight
- Source and destination addresses
- Carrier availability
- Service level requirements

### Example Rate Calculation

1. Product dimensions:
```json
{
    "length": "10",
    "width": "8",
    "height": "6",
    "weight": "2",
    "distance_unit": "in",
    "mass_unit": "lb"
}
```

2. Available rates returned:
```json
{
    "rates": [
        {
            "provider": "USPS",
            "service": "Priority Mail",
            "amount": "12.99",
            "estimated_days": 2
        },
        {
            "provider": "UPS",
            "service": "Ground",
            "amount": "15.99",
            "estimated_days": 4
        }
    ]
}
```

## Label Generation

Labels are generated after:
1. Order is paid
2. Addresses are validated
3. Shipping rate is selected
4. Carrier service is confirmed

### Label Generation Process
1. Create addresses in Shippo
2. Validate addresses
3. Create parcel
4. Get shipping rates
5. Create transaction
6. Generate label

## Status Tracking

### Shipping Status Codes
```python
SHIPPING_STATUS = (
    ('PENDING', 'Label created, awaiting pickup'),
    ('TRANSIT', 'Package in transit'),
    ('DELIVERED', 'Package delivered'),
    ('RETURNED', 'Package returned to sender'),
    ('FAILURE', 'Delivery failed')
)
```

### Status History Example
```json
{
    "shipping_id": "789e4567-e89b-12d3-a456-426614174000",
    "status_history": [
        {
            "status": "PENDING",
            "description": "Label created",
            "created_at": "2025-02-19T10:00:00Z"
        },
        {
            "status": "TRANSIT",
            "description": "Package picked up",
            "created_at": "2025-02-20T10:00:00Z"
        },
        {
            "status": "DELIVERED",
            "description": "Package delivered",
            "created_at": "2025-02-22T14:30:00Z"
        }
    ]
}
```

## Error Handling

### Common Error Responses

1. Address Validation Error:
```json
{
    "error": "Address validation failed",
    "details": "The address as submitted could not be found"
}
```

2. Rate Calculation Error:
```json
{
    "error": "Failed to calculate shipping rates",
    "details": "No rates available for this route"
}
```

3. Label Creation Error:
```json
{
    "error": "Failed to create shipping label",
    "details": "Transaction failed with carrier"
}
```

### Error Prevention
1. Validate addresses before saving
2. Check product dimensions
3. Verify carrier availability
4. Ensure order is paid
5. Validate shipping rates

---
*Last Updated: February 20, 2025* 