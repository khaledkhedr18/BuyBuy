# BuyBuy E-Commerce API Specification

## API Overview

The BuyBuy E-Commerce API provides comprehensive endpoints for managing products, categories, users, and authentication. The API follows RESTful principles and uses JSON for data exchange.

### Base URL

```
Development: http://localhost:8000/api/v1/
Production: https://api.buybuy.com/v1/
```

### Authentication

The API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

## Common Response Formats

### Success Response

```json
{
  "success": true,
  "data": {},
  "message": "Operation completed successfully",
  "errors": [],
  "meta": {
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 100,
      "total_pages": 5
    }
  }
}
```

### Error Response

```json
{
  "success": false,
  "data": null,
  "message": "Validation failed",
  "errors": [
    {
      "field": "email",
      "message": "This field is required"
    }
  ],
  "meta": {}
}
```

## Authentication Endpoints

### Register User

**POST** `/auth/register/`

Register a new user account.

**Request Body:**

```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "securepassword123",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "username": "johndoe",
      "email": "john@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "is_active": true
    },
    "tokens": {
      "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
      "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
  },
  "message": "User registered successfully"
}
```

### Login User

**POST** `/auth/login/`

Authenticate user and return JWT tokens.

**Request Body:**

```json
{
  "username": "johndoe",
  "password": "securepassword123"
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "username": "johndoe",
      "email": "john@example.com",
      "first_name": "John",
      "last_name": "Doe"
    },
    "tokens": {
      "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
      "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
  },
  "message": "Login successful"
}
```

### Refresh Token

**POST** `/auth/refresh/`

Refresh access token using refresh token.

**Request Body:**

```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  },
  "message": "Token refreshed successfully"
}
```

### Logout User

**POST** `/auth/logout/`

Logout user and invalidate refresh token.

**Headers:**

```
Authorization: Bearer <access-token>
```

**Request Body:**

```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response:**

```json
{
  "success": true,
  "data": null,
  "message": "Logout successful"
}
```

## User Endpoints

### Get User Profile

**GET** `/users/profile/`

Get current user's profile information.

**Headers:**

```
Authorization: Bearer <access-token>
```

**Response:**

```json
{
  "success": true,
  "data": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+1234567890",
    "address": "123 Main St",
    "city": "New York",
    "country": "USA",
    "is_active": true,
    "date_joined": "2024-01-01T00:00:00Z"
  }
}
```

### Update User Profile

**PUT** `/users/profile/`

Update current user's profile information.

**Headers:**

```
Authorization: Bearer <access-token>
```

**Request Body:**

```json
{
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "address": "123 Main St",
  "city": "New York",
  "country": "USA"
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+1234567890",
    "address": "123 Main St",
    "city": "New York",
    "country": "USA",
    "is_active": true,
    "date_joined": "2024-01-01T00:00:00Z"
  },
  "message": "Profile updated successfully"
}
```

## Category Endpoints

### List Categories

**GET** `/categories/`

Get list of all categories with optional filtering.

**Query Parameters:**

- `parent` (optional): Filter by parent category ID
- `is_active` (optional): Filter by active status (true/false)
- `search` (optional): Search categories by name
- `page` (optional): Page number for pagination (default: 1)
- `per_page` (optional): Items per page (default: 20, max: 100)

**Response:**

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "Electronics",
      "description": "Electronic devices and accessories",
      "slug": "electronics",
      "parent": null,
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    },
    {
      "id": 2,
      "name": "Smartphones",
      "description": "Mobile phones and accessories",
      "slug": "smartphones",
      "parent": 1,
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "meta": {
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 2,
      "total_pages": 1
    }
  }
}
```

### Create Category

**POST** `/categories/`

Create a new category (Admin only).

**Headers:**

```
Authorization: Bearer <admin-access-token>
```

**Request Body:**

```json
{
  "name": "Laptops",
  "description": "Laptop computers and accessories",
  "parent": 1,
  "is_active": true
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "id": 3,
    "name": "Laptops",
    "description": "Laptop computers and accessories",
    "slug": "laptops",
    "parent": 1,
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  },
  "message": "Category created successfully"
}
```

### Get Category Details

**GET** `/categories/{id}/`

Get detailed information about a specific category.

**Response:**

```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "Electronics",
    "description": "Electronic devices and accessories",
    "slug": "electronics",
    "parent": null,
    "is_active": true,
    "children": [
      {
        "id": 2,
        "name": "Smartphones",
        "slug": "smartphones"
      },
      {
        "id": 3,
        "name": "Laptops",
        "slug": "laptops"
      }
    ],
    "product_count": 150,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

### Update Category

**PUT** `/categories/{id}/`

Update a category (Admin only).

**Headers:**

```
Authorization: Bearer <admin-access-token>
```

**Request Body:**

```json
{
  "name": "Electronics & Gadgets",
  "description": "Electronic devices, gadgets and accessories",
  "is_active": true
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "Electronics & Gadgets",
    "description": "Electronic devices, gadgets and accessories",
    "slug": "electronics-gadgets",
    "parent": null,
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z"
  },
  "message": "Category updated successfully"
}
```

### Delete Category

**DELETE** `/categories/{id}/`

Delete a category (Admin only).

**Headers:**

```
Authorization: Bearer <admin-access-token>
```

**Response:**

```json
{
  "success": true,
  "data": null,
  "message": "Category deleted successfully"
}
```

## Product Endpoints

### List Products

**GET** `/products/`

Get list of products with advanced filtering, sorting, and pagination.

**Query Parameters:**

- `category` (optional): Filter by category ID
- `min_price` (optional): Minimum price filter
- `max_price` (optional): Maximum price filter
- `is_active` (optional): Filter by active status (true/false)
- `in_stock` (optional): Filter by stock availability (true/false)
- `search` (optional): Search products by name or description
- `sort` (optional): Sort by field (name, price, created_at, updated_at)
- `order` (optional): Sort order (asc, desc)
- `page` (optional): Page number for pagination (default: 1)
- `per_page` (optional): Items per page (default: 20, max: 100)

**Example Request:**

```
GET /products/?category=1&min_price=100&max_price=1000&sort=price&order=asc&page=1&per_page=20
```

**Response:**

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "iPhone 15 Pro",
      "description": "Latest iPhone with advanced features",
      "price": 999.99,
      "category": {
        "id": 2,
        "name": "Smartphones",
        "slug": "smartphones"
      },
      "stock_quantity": 50,
      "is_active": true,
      "images": [
        {
          "id": 1,
          "image_url": "https://example.com/images/iphone15pro.jpg",
          "alt_text": "iPhone 15 Pro front view",
          "is_primary": true
        }
      ],
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "meta": {
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 150,
      "total_pages": 8
    },
    "filters": {
      "applied": {
        "category": 1,
        "min_price": 100,
        "max_price": 1000
      },
      "available": {
        "categories": [
          { "id": 1, "name": "Electronics", "count": 150 },
          { "id": 2, "name": "Smartphones", "count": 50 }
        ],
        "price_range": {
          "min": 10.99,
          "max": 2999.99
        }
      }
    }
  }
}
```

### Create Product

**POST** `/products/`

Create a new product (Admin only).

**Headers:**

```
Authorization: Bearer <admin-access-token>
Content-Type: multipart/form-data
```

**Request Body (multipart/form-data):**

```
name: MacBook Pro 16"
description: High-performance laptop for professionals
price: 2499.99
category: 3
stock_quantity: 25
is_active: true
images: [file1.jpg, file2.jpg]
```

**Response:**

```json
{
  "success": true,
  "data": {
    "id": 2,
    "name": "MacBook Pro 16\"",
    "description": "High-performance laptop for professionals",
    "price": 2499.99,
    "category": {
      "id": 3,
      "name": "Laptops",
      "slug": "laptops"
    },
    "stock_quantity": 25,
    "is_active": true,
    "images": [
      {
        "id": 2,
        "image_url": "https://example.com/images/macbookpro.jpg",
        "alt_text": "MacBook Pro 16 inch",
        "is_primary": true
      }
    ],
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  },
  "message": "Product created successfully"
}
```

### Get Product Details

**GET** `/products/{id}/`

Get detailed information about a specific product.

**Response:**

```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "iPhone 15 Pro",
    "description": "Latest iPhone with advanced features including A17 Pro chip, titanium design, and advanced camera system.",
    "price": 999.99,
    "category": {
      "id": 2,
      "name": "Smartphones",
      "slug": "smartphones"
    },
    "stock_quantity": 50,
    "is_active": true,
    "images": [
      {
        "id": 1,
        "image_url": "https://example.com/images/iphone15pro.jpg",
        "alt_text": "iPhone 15 Pro front view",
        "is_primary": true
      },
      {
        "id": 2,
        "image_url": "https://example.com/images/iphone15pro_back.jpg",
        "alt_text": "iPhone 15 Pro back view",
        "is_primary": false
      }
    ],
    "specifications": {
      "display": "6.1-inch Super Retina XDR",
      "processor": "A17 Pro chip",
      "storage": "128GB",
      "camera": "48MP Main camera"
    },
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

### Update Product

**PUT** `/products/{id}/`

Update a product (Admin only).

**Headers:**

```
Authorization: Bearer <admin-access-token>
```

**Request Body:**

```json
{
  "name": "iPhone 15 Pro Max",
  "description": "Latest iPhone with advanced features and larger display",
  "price": 1099.99,
  "stock_quantity": 30,
  "is_active": true
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "iPhone 15 Pro Max",
    "description": "Latest iPhone with advanced features and larger display",
    "price": 1099.99,
    "category": {
      "id": 2,
      "name": "Smartphones",
      "slug": "smartphones"
    },
    "stock_quantity": 30,
    "is_active": true,
    "images": [
      {
        "id": 1,
        "image_url": "https://example.com/images/iphone15pro.jpg",
        "alt_text": "iPhone 15 Pro front view",
        "is_primary": true
      }
    ],
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z"
  },
  "message": "Product updated successfully"
}
```

### Delete Product

**DELETE** `/products/{id}/`

Delete a product (Admin only).

**Headers:**

```
Authorization: Bearer <admin-access-token>
```

**Response:**

```json
{
  "success": true,
  "data": null,
  "message": "Product deleted successfully"
}
```

## Error Codes

### HTTP Status Codes

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation errors
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

### Common Error Messages

- `INVALID_CREDENTIALS`: Invalid username or password
- `TOKEN_EXPIRED`: JWT token has expired
- `TOKEN_INVALID`: JWT token is invalid
- `PERMISSION_DENIED`: User lacks required permissions
- `VALIDATION_ERROR`: Request data validation failed
- `RESOURCE_NOT_FOUND`: Requested resource does not exist
- `RATE_LIMIT_EXCEEDED`: Too many requests from this IP/user

## Rate Limiting

The API implements rate limiting to ensure fair usage:

- **Authentication endpoints**: 5 requests per minute per IP
- **General API endpoints**: 100 requests per minute per authenticated user
- **Admin endpoints**: 200 requests per minute per admin user

Rate limit headers are included in responses:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## Pagination

All list endpoints support pagination with the following parameters:

- `page`: Page number (default: 1)
- `per_page`: Items per page (default: 20, max: 100)

Pagination information is included in the response meta object.

## Filtering and Sorting

### Available Filters

- **Products**: category, price range, stock availability, active status, search
- **Categories**: parent category, active status, search

### Available Sort Fields

- **Products**: name, price, created_at, updated_at
- **Categories**: name, created_at, updated_at

### Sort Order

- `asc`: Ascending order (default)
- `desc`: Descending order

## Search

Search functionality is available for products and categories:

- **Products**: Searches in name and description fields
- **Categories**: Searches in name and description fields

Search is case-insensitive and supports partial matches.
