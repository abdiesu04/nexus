# Products API Documentation

## Table of Contents
1. [Overview](#overview)
2. [Models](#models)
3. [API Endpoints](#api-endpoints)
4. [Pagination](#pagination)
5. [Search & Filtering](#search--filtering)
6. [Permissions](#permissions)
7. [Testing Examples](#testing-examples)

## Overview

The Products API provides functionality for managing product categories and product listings in the marketplace. It supports:
- Category management (hierarchical structure)
- Product listing management with multiple images (up to 5 per product)
- Advanced search and filtering capabilities
- Pagination for efficient data retrieval
- Seller-specific product management
- Shipping information handling
- Image management (primary image, deletion)

## Models

### Category Model
```python
class Category:
    id: UUID (primary key)
    name: string (unique)
    description: text (optional)
    parent: Category (optional, for subcategories)
```

### Product Model
```python
class Product:
    id: UUID (primary key)
    title: string
    description: text
    price: decimal(10,2)
    category: Category (foreign key)
    seller: User (foreign key)
    stock: integer
    
    # Shipping Details
    weight: decimal(10,2) (in pounds)
    length: decimal(10,2) (in inches)
    width: decimal(10,2) (in inches)
    height: decimal(10,2) (in inches)
    free_shipping: boolean
    requires_shipping: boolean
    
    # Metadata
    created_at: datetime
    updated_at: datetime
```

### ProductImage Model
```python
class ProductImage:
    id: UUID (primary key)
    product: Product (foreign key)
    image: file
    is_primary: boolean
    created_at: datetime
```

## API Endpoints

### Categories

#### 1. List Categories
**Endpoint:** `GET /products/categories/`
- Public access
- Supports pagination
- Supports search by name and description
- Returns paginated categories

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Number of items per page (default: 10, max: 100)
- `search`: Search term for name or description

**Response (200 OK):**
```json
{
    "count": 10,
    "next": "http://api.example.com/products/categories/?page=2",
    "previous": null,
    "results": [
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "name": "Electronics",
            "description": "Electronic devices and accessories",
            "parent": null
        }
    ]
}
```

### Products

#### 1. List Products
**Endpoint:** `GET /products/products/`
- Public access
- Supports pagination, filtering, searching, and ordering
- Returns paginated products

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Number of items per page (default: 10, max: 100)
- `search`: Search term for title, description, category name, or seller username
- `ordering`: Field to order by (prefix with '-' for descending)
  - Available fields: price, created_at, stock, title
- **Filters:**
  - `min_price`: Minimum price
  - `max_price`: Maximum price
  - `category_name`: Filter by category name (partial match)
  - `seller_name`: Filter by seller username (partial match)
  - `created_after`: Filter by creation date (ISO format)
  - `created_before`: Filter by creation date (ISO format)
  - `requires_shipping`: Filter by shipping requirement (true/false)
  - `free_shipping`: Filter by free shipping (true/false)
  - `title`: Filter by title (partial match)
  - `description`: Filter by description (partial match)
  - `stock`: Filter by stock amount
  - `category`: Filter by category ID
  - `seller`: Filter by seller ID

**Response (200 OK):**
```json
{
    "count": 100,
    "next": "http://api.example.com/products/products/?page=2",
    "previous": null,
    "results": [
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "title": "Smartphone X",
            "description": "Latest smartphone model",
            "price": "999.99",
            "category": "123e4567-e89b-12d3-a456-426614174001",
            "seller": "123e4567-e89b-12d3-a456-426614174000",
            "stock": 50,
            "weight": "0.50",
            "length": "6.00",
            "width": "3.00",
            "height": "0.50",
            "free_shipping": false,
            "requires_shipping": true,
            "created_at": "2025-03-04T10:00:00Z",
            "updated_at": "2025-03-04T10:00:00Z",
            "images": [
                {
                    "id": "123e4567-e89b-12d3-a456-426614174010",
                    "image": "http://api.example.com/media/products/phone-main.jpg",
                    "is_primary": true,
                    "created_at": "2025-03-04T10:00:00Z"
                }
            ]
        }
    ]
}
```

#### 2. Create Product (Seller Only)
**Endpoint:** `POST /products/products/`

**Request Body (multipart/form-data):**
```json
{
    "title": "New Product",
    "description": "Product description",
    "price": "99.99",
    "category": "123e4567-e89b-12d3-a456-426614174001",
    "stock": 100,
    "weight": "1.50",
    "length": "10.00",
    "width": "5.00",
    "height": "2.00",
    "free_shipping": false,
    "requires_shipping": true,
    "uploaded_images": [<file1>, <file2>, <file3>]  // Up to 5 images
}
```

#### 3. Set Primary Image
**Endpoint:** `POST /products/products/{product_id}/set_primary_image/`

**Request Body:**
```json
{
    "image_id": "123e4567-e89b-12d3-a456-426614174010"
}
```

**Response (200 OK):**
```json
{
    "id": "123e4567-e89b-12d3-a456-426614174010",
    "image": "http://api.example.com/media/products/phone-main.jpg",
    "is_primary": true,
    "created_at": "2025-03-04T10:00:00Z"
}
```

#### 4. Delete Image
**Endpoint:** `DELETE /products/products/{product_id}/delete_image/`

**Request Body:**
```json
{
    "image_id": "123e4567-e89b-12d3-a456-426614174010"
}
```

**Response (204 No Content)**

## Pagination

All list endpoints support pagination with the following parameters:
- `page`: Page number (default: 1)
- `page_size`: Number of items per page (default: 10, max: 100)

Paginated responses include:
- `count`: Total number of items
- `next`: URL for next page (null if none)
- `previous`: URL for previous page (null if none)
- `results`: Array of items for current page

## Search & Filtering

### Search
Use the `search` parameter to perform text search across multiple fields:
```bash
# Search products
GET /products/products/?search=smartphone

# Search categories
GET /products/categories/?search=electronics
```

### Filtering
Products can be filtered using various parameters:
```bash
# Price range
GET /products/products/?min_price=100&max_price=1000

# Category
GET /products/products/?category_name=electronics

# Date range
GET /products/products/?created_after=2025-01-01T00:00:00Z&created_before=2025-12-31T23:59:59Z

# Shipping options
GET /products/products/?requires_shipping=true&free_shipping=false

```

### Ordering
Products can be ordered by specific fields:
```bash
# Order by price (ascending)
GET /products/products/?ordering=price

# Order by price (descending)
GET /products/products/?ordering=-price

# Order by creation date
GET /products/products/?ordering=-created_at

# Order by title
GET /products/products/?ordering=title
```

## Permissions

### Category Endpoints
| Endpoint | Method | Permission |
|----------|---------|------------|
| `/categories/` | GET | Public |
| `/categories/` | POST | Seller/Admin |
| `/categories/{id}/` | GET | Public |
| `/categories/{id}/` | PUT/PATCH | Seller/Admin |
| `/categories/{id}/` | DELETE | Seller/Admin |

### Product Endpoints
| Endpoint | Method | Permission |
|----------|---------|------------|
| `/products/` | GET | Public |
| `/products/` | POST | Seller/Admin |
| `/products/{id}/` | GET | Public |
| `/products/{id}/` | PUT/PATCH | Owner/Admin |
| `/products/{id}/` | DELETE | Owner/Admin |
| `/products/{id}/set_primary_image/` | POST | Owner/Admin |
| `/products/{id}/delete_image/` | DELETE | Owner/Admin |

## Testing Examples

### 1. List Products with Filtering and Pagination
```bash
# Get second page of products in electronics category
curl -X GET "http://localhost:8000/products/products/?page=2&page_size=20&category_name=electronics&min_price=100&ordering=-price" \
  -H "Content-Type: application/json"
```

### 2. Search Products
```bash
# Search for smartphones with free shipping
curl -X GET "http://localhost:8000/products/products/?search=smartphone&free_shipping=true" \
  -H "Content-Type: application/json"
```

### 3. Create Product with Images
```bash
curl -X POST http://localhost:8000/products/products/ \
  -H "Authorization: Bearer your_access_token" \
  -H "Content-Type: multipart/form-data" \
  -F "title=New Product" \
  -F "description=Product description" \
  -F "price=99.99" \
  -F "category=123e4567-e89b-12d3-a456-426614174001" \
  -F "stock=100" \
  -F "weight=1.50" \
  -F "length=10.00" \
  -F "width=5.00" \
  -F "height=2.00" \
  -F "requires_shipping=true" \
  -F "uploaded_images=@image1.jpg" \
  -F "uploaded_images=@image2.jpg"
```

### 4. Set Primary Image
```bash
curl -X POST http://localhost:8000/products/products/123e4567-e89b-12d3-a456-426614174003/set_primary_image/ \
  -H "Authorization: Bearer your_access_token" \
  -H "Content-Type: application/json" \
  -d '{
    "image_id": "123e4567-e89b-12d3-a456-426614174010"
  }'
```

### 5. Delete Image
```bash
curl -X DELETE http://localhost:8000/products/products/123e4567-e89b-12d3-a456-426614174003/delete_image/ \
  -H "Authorization: Bearer your_access_token" \
  -H "Content-Type: application/json" \
  -d '{
    "image_id": "123e4567-e89b-12d3-a456-426614174010"
  }'
```

## Error Responses

### 401 Unauthorized
```json
{
    "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
    "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
    "detail": "Not found."
}
```

### 400 Bad Request
```json
{
    "price": ["Ensure that there are no more than 2 decimal places."],
    "category": ["This field is required."],
    "uploaded_images": "You can upload a maximum of 5 images."
}
```

### 400 Bad Request - Adding Too Many Images
```json
{
    "uploaded_images": "This product already has 3 images. You can only add 2 more."
}
```

### 404 Not Found - Image Not Found
```json
{
    "detail": "Image not found"
}
```

---
*Last Updated: March 4, 2025* 