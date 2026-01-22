# Luli Jewelry - User API Guide

Welcome to Luli Jewelry API! This guide will help you integrate with our jewelry e-commerce platform and use all available features.

## Base URL
```
http://localhost:8000
```

## Authentication

This API uses JWT (JSON Web Token) authentication. After logging in, include the access token in all authenticated requests:

```
Authorization: Bearer <access_token>
```

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Browsing Products](#browsing-products)
3. [Shopping Cart](#shopping-cart)
4. [Wishlist](#wishlist)
5. [Placing Orders](#placing-orders)
6. [Stripe Payments](#stripe-payments)
7. [Managing Your Account](#managing-your-account)
8. [Product Reviews](#product-reviews)
9. [Search & Filters](#search--filters)
10. [Coupons & Discounts](#coupons--discounts)
11. [Error Handling](#error-handling)

---

## Getting Started

### 1. Register a New Account

**Endpoint:** `POST /auth/register/`

**Description:** Create a new user account

**Request:**
```json
{
    "loginname": "john_doe",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "password": "securepassword123"
}
```

**Response (201 Created):**
```json
{
    "detail": "User created. Check your email to verify."
}
```

**Example using cURL:**
```bash
curl -X POST http://localhost:8000/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "loginname": "john_doe",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "password": "securepassword123"
  }'
```

---

### 2. Verify Email

**Endpoint:** `GET /auth/verify-email/?uid={uid}&token={token}`

**Description:** Verify your email address using the link sent to your email

**Query Parameters:**
- `uid`: User ID from the verification email
- `token`: Verification token from the email

**Response (200 OK):**
```json
{
    "detail": "Email verified successfully."
}
```

**Example:**
```
GET http://localhost:8000/auth/verify-email/?uid=1&token=abc123def456
```

---

### 3. Login

**Endpoint:** `POST /auth/login/`

**Description:** Authenticate and receive JWT tokens

**Request:**
```json
{
    "username": "john_doe",
    "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
    "message": "Login successful.",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "id": 1,
    "loginname": "john_doe",
    "email": "john.doe@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "is_staff": false,
    "is_superuser": false
}
```

**Example using cURL:**
```bash
curl -X POST http://localhost:8000/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "securepassword123"
  }'
```

**Important:** Save the `access` token - you'll need it for all authenticated requests!

---

### 4. Logout

**Endpoint:** `POST /auth/logout/`

**Description:** Logout and invalidate refresh token

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request:**
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response (200 OK):**
```json
{
    "detail": "Logout successful."
}
```

---

## Browsing Products

### 1. Get All Products

**Endpoint:** `GET /products/`

**Description:** Get a list of all products with filtering and pagination

**Query Parameters:**
- `category`: Filter by category slug (e.g., `rings`)
- `material`: Filter by material name (e.g., `Gold`)
- `gemstone`: Filter by gemstone name (e.g., `Diamond`)
- `min_price`: Minimum price (e.g., `100`)
- `max_price`: Maximum price (e.g., `1000`)
- `jewelry_type`: Filter by type (`ring`, `necklace`, `earring`, `bracelet`)
- `is_featured`: Filter featured products (`true`/`false`)
- `is_customizable`: Filter customizable products (`true`/`false`)
- `search`: Search in title and description
- `ordering`: Sort order (`price`, `-price`, `created_at`, `-created_at`)
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)

**Example Request:**
```
GET http://localhost:8000/products/?category=rings&min_price=100&max_price=500&ordering=-price&page=1
```

**Response (200 OK):**
```json
{
    "count": 25,
    "next": "http://localhost:8000/products/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "title": "Classic Gold Wedding Ring",
            "slug": "classic-gold-wedding-ring",
            "description": "A timeless 18K gold wedding band.",
            "price": "299.99",
            "stock_quantity": 50,
            "is_featured": true,
            "jewelry_type": "ring",
            "weight": "3.5",
            "dimensions": "2mm band width",
            "is_customizable": false,
            "category": {
                "id": 6,
                "name": "Wedding Rings",
                "slug": "wedding-rings"
            },
            "primary_material": {
                "id": 1,
                "name": "Gold",
                "is_precious": true
            },
            "images": [
                {
                    "id": 1,
                    "image": "/media/products/classic_gold_wedding_ring.jpg",
                    "alt_text": "Classic Gold Wedding Ring image",
                    "is_main": true
                }
            ],
            "average_rating": 4.5,
            "review_count": 3,
            "created_at": "2024-01-01T10:00:00Z"
        }
    ]
}
```

---

### 2. Get Product Details

**Endpoint:** `GET /products/{slug}/`

**Description:** Get detailed information about a specific product

**Example Request:**
```
GET http://localhost:8000/products/classic-gold-wedding-ring/
```

**Response (200 OK):**
```json
{
    "id": 1,
    "title": "Classic Gold Wedding Ring",
    "slug": "classic-gold-wedding-ring",
    "description": "A timeless 18K gold wedding band.",
    "studio_notes": "Hand-polished finish.",
    "price": "299.99",
    "stock_quantity": 50,
    "is_featured": true,
    "jewelry_type": "ring",
    "weight": "3.5",
    "dimensions": "2mm band width",
    "is_customizable": false,
    "customization_options": {},
    "care_instructions": "Clean with soft cloth.",
    "category": {
        "id": 6,
        "name": "Wedding Rings",
        "slug": "wedding-rings"
    },
    "primary_material": {
        "id": 1,
        "name": "Gold",
        "is_precious": true,
        "description": "24K, 18K, 14K Gold"
    },
    "secondary_materials": [],
    "gemstones": [],
    "images": [
        {
            "id": 1,
            "image": "/media/products/classic_gold_wedding_ring.jpg",
            "alt_text": "Classic Gold Wedding Ring image",
            "is_main": true
        }
    ],
    "reviews": [
        {
            "id": 1,
            "user": {
                "id": 1,
                "loginname": "john_doe",
                "first_name": "John",
                "last_name": "Doe"
            },
            "rating": 5,
            "comment": "Beautiful ring!",
            "status": 1,
            "created_at": "2024-01-01T10:00:00Z"
        }
    ],
    "average_rating": 4.5,
    "review_count": 3,
    "created_at": "2024-01-01T10:00:00Z"
}
```

---

### 3. Get Featured Products

**Endpoint:** `GET /products/featured/`

**Description:** Get all featured products

**Example Request:**
```
GET http://localhost:8000/products/featured/
```

**Response (200 OK):**
```json
[
    {
        "id": 1,
        "title": "Classic Gold Wedding Ring",
        "slug": "classic-gold-wedding-ring",
        "price": "299.99",
        "images": [
            {
                "image": "/media/products/classic_gold_wedding_ring.jpg",
                "alt_text": "Classic Gold Wedding Ring image",
                "is_main": true
            }
        ],
        "average_rating": 4.5,
        "review_count": 3
    }
]
```

---

### 4. Get Related Products

**Endpoint:** `GET /products/{slug}/related/`

**Description:** Get products related to the specified product

**Example Request:**
```
GET http://localhost:8000/products/classic-gold-wedding-ring/related/
```

**Response (200 OK):**
```json
[
    {
        "id": 2,
        "title": "Diamond Engagement Ring",
        "slug": "diamond-engagement-ring",
        "price": "1299.99",
        "images": [
            {
                "image": "/media/products/diamond_engagement_ring.jpg",
                "alt_text": "Diamond Engagement Ring image",
                "is_main": true
            }
        ],
        "average_rating": 4.8,
        "review_count": 5,
        "reason": "Similar style"
    }
]
```

---

### 5. Get Categories

**Endpoint:** `GET /categories/`

**Description:** Get list of all product categories

**Query Parameters:**
- `parent`: Filter by parent category name
- `search`: Search in category name and description

**Example Request:**
```
GET http://localhost:8000/categories/
```

**Response (200 OK):**
```json
[
    {
        "id": 1,
        "name": "Rings",
        "slug": "rings",
        "description": "Beautiful rings for every occasion",
        "parent": null,
        "created_at": "2024-01-01T10:00:00Z"
    },
    {
        "id": 5,
        "name": "Engagement Rings",
        "slug": "engagement-rings",
        "description": "Special engagement rings",
        "parent": {
            "id": 1,
            "name": "Rings",
            "slug": "rings"
        },
        "created_at": "2024-01-01T10:00:00Z"
    }
]
```

---

### 6. Get Products by Category

**Endpoint:** `GET /get-products/`

**Description:** Get products by category with specified count

**Query Parameters:**
- `category`: Category slug (required)
- `count`: Number of products to return (optional, default: 4)

**Example Request:**
```
GET http://localhost:8000/get-products/?category=bride-groom-collection&count=4
```

**Response (200 OK):**
```json
[
    {
        "id": 1,
        "name": "Classic Gold Wedding Ring",
        "slug": "classic-gold-wedding-ring",
        "price": "299.99",
        "image": "/media/products/classic_gold_wedding_ring.jpg"
    },
    {
        "id": 2,
        "name": "Diamond Engagement Ring",
        "slug": "diamond-engagement-ring",
        "price": "1299.99",
        "image": "/media/products/diamond_engagement_ring.jpg"
    }
]
```

---

## Shopping Cart

### 1. Get Cart

**Endpoint:** `GET /cart/`

**Description:** Get your shopping cart with all items

**Headers:**
```
Authorization: Bearer <access_token>
```

**Example Request:**
```bash
curl -X GET http://localhost:8000/cart/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response (200 OK):**
```json
{
    "id": 1,
    "user": 1,
    "total_price": "599.98",
    "total_items": 2,
    "items": [
        {
            "id": 1,
            "product": {
                "id": 1,
                "title": "Classic Gold Wedding Ring",
                "slug": "classic-gold-wedding-ring",
                "price": "299.99",
                "images": [
                    {
                        "image": "/media/products/classic_gold_wedding_ring.jpg",
                        "alt_text": "Classic Gold Wedding Ring image",
                        "is_main": true
                    }
                ]
            },
            "quantity": 1,
            "total_price": "299.99"
        },
        {
            "id": 2,
            "product": {
                "id": 2,
                "title": "Diamond Engagement Ring",
                "slug": "diamond-engagement-ring",
                "price": "1299.99",
                "images": [
                    {
                        "image": "/media/products/diamond_engagement_ring.jpg",
                        "alt_text": "Diamond Engagement Ring image",
                        "is_main": true
                    }
                ]
            },
            "quantity": 1,
            "total_price": "1299.99"
        }
    ],
    "created_at": "2024-01-01T10:00:00Z",
    "updated_at": "2024-01-01T10:00:00Z"
}
```

---

### 2. Add Item to Cart

**Endpoint:** `POST /cart/`

**Description:** Add a product to your cart

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request:**
```json
{
    "product": 1,
    "quantity": 2
}
```

**Example Request:**
```bash
curl -X POST http://localhost:8000/cart/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product": 1,
    "quantity": 2
  }'
```

**Response (201 Created):**
```json
{
    "id": 3,
    "product": {
        "id": 1,
        "title": "Classic Gold Wedding Ring",
        "slug": "classic-gold-wedding-ring",
        "price": "299.99",
        "images": [
            {
                "image": "/media/products/classic_gold_wedding_ring.jpg",
                "alt_text": "Classic Gold Wedding Ring image",
                "is_main": true
            }
        ]
    },
    "quantity": 2,
    "total_price": "599.98"
}
```

---

### 3. Update Cart Item

**Endpoint:** `PUT /cart/{item_id}/`

**Description:** Update the quantity of an item in your cart

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request:**
```json
{
    "quantity": 3
}
```

**Example Request:**
```bash
curl -X PUT http://localhost:8000/cart/1/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "quantity": 3
  }'
```

**Response (200 OK):**
```json
{
    "id": 1,
    "product": {
        "id": 1,
        "title": "Classic Gold Wedding Ring",
        "slug": "classic-gold-wedding-ring",
        "price": "299.99"
    },
    "quantity": 3,
    "total_price": "899.97"
}
```

---

### 4. Remove Cart Item

**Endpoint:** `DELETE /cart/{item_id}/`

**Description:** Remove an item from your cart

**Headers:**
```
Authorization: Bearer <access_token>
```

**Example Request:**
```bash
curl -X DELETE http://localhost:8000/cart/1/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response (204 No Content):**
```
No content
```

---

## Wishlist

### 1. Get Wishlist

**Endpoint:** `GET /wishlist/`

**Description:** Get your wishlist with all saved items

**Headers:**
```
Authorization: Bearer <access_token>
```

**Example Request:**
```bash
curl -X GET http://localhost:8000/wishlist/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response (200 OK):**
```json
{
    "id": 1,
    "user": 1,
    "items": [
        {
            "id": 1,
            "product": {
                "id": 3,
                "title": "Pearl Drop Earrings",
                "slug": "pearl-drop-earrings",
                "price": "89.99",
                "images": [
                    {
                        "image": "/media/products/pearl_drop_earrings.jpg",
                        "alt_text": "Pearl Drop Earrings image",
                        "is_main": true
                    }
                ]
            },
            "created_at": "2024-01-01T10:00:00Z"
        }
    ],
    "created_at": "2024-01-01T10:00:00Z",
    "updated_at": "2024-01-01T10:00:00Z"
}
```

---

### 2. Add to Wishlist

**Endpoint:** `POST /wishlist/`

**Description:** Add a product to your wishlist

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request:**
```json
{
    "product": 3
}
```

**Example Request:**
```bash
curl -X POST http://localhost:8000/wishlist/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product": 3
  }'
```

**Response (201 Created):**
```json
{
    "id": 2,
    "product": {
        "id": 3,
        "title": "Pearl Drop Earrings",
        "slug": "pearl-drop-earrings",
        "price": "89.99",
        "images": [
            {
                "image": "/media/products/pearl_drop_earrings.jpg",
                "alt_text": "Pearl Drop Earrings image",
                "is_main": true
            }
        ]
    },
    "created_at": "2024-01-01T10:00:00Z"
}
```

---

### 3. Remove from Wishlist

**Endpoint:** `DELETE /wishlist/{item_id}/`

**Description:** Remove an item from your wishlist

**Headers:**
```
Authorization: Bearer <access_token>
```

**Example Request:**
```bash
curl -X DELETE http://localhost:8000/wishlist/1/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response (204 No Content):**
```
No content
```

---

## Placing Orders

### 1. Create Order

**Endpoint:** `POST /orders/create/`

**Description:** Create a new order from your cart

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request:**
```json
{
    "shipping_address": {
        "first_name": "John",
        "last_name": "Doe",
        "address_line_1": "123 Main St",
        "city": "New York",
        "state": "NY",
        "postal_code": "10001",
        "country": "USA",
        "phone": "555-123-4567"
    },
    "billing_address": {
        "first_name": "John",
        "last_name": "Doe",
        "address_line_1": "123 Main St",
        "city": "New York",
        "state": "NY",
        "postal_code": "10001",
        "country": "USA",
        "phone": "555-123-4567"
    },
    "notes": "Please handle with care"
}
```

**Example Request:**
```bash
curl -X POST http://localhost:8000/orders/create/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "shipping_address": {
        "first_name": "John",
        "last_name": "Doe",
        "address_line_1": "123 Main St",
        "city": "New York",
        "state": "NY",
        "postal_code": "10001",
        "country": "USA",
        "phone": "555-123-4567"
    },
    "billing_address": {
        "first_name": "John",
        "last_name": "Doe",
        "address_line_1": "123 Main St",
        "city": "New York",
        "state": "NY",
        "postal_code": "10001",
        "country": "USA",
        "phone": "555-123-4567"
    },
    "notes": "Please handle with care"
  }'
```

**Response (201 Created):**
```json
{
    "id": 1,
    "order_number": "ORD-20240101-001",
    "status": "pending",
    "payment_status": "pending",
    "subtotal": "299.99",
    "tax_amount": "15.00",
    "shipping_cost": "10.00",
    "total_amount": "324.99",
    "shipping_address": {
        "first_name": "John",
        "last_name": "Doe",
        "address_line_1": "123 Main St",
        "city": "New York",
        "state": "NY",
        "postal_code": "10001",
        "country": "USA",
        "phone": "555-123-4567"
    },
    "billing_address": {
        "first_name": "John",
        "last_name": "Doe",
        "address_line_1": "123 Main St",
        "city": "New York",
        "state": "NY",
        "postal_code": "10001",
        "country": "USA",
        "phone": "555-123-4567"
    },
    "items": [
        {
            "id": 1,
            "product": {
                "id": 1,
                "title": "Classic Gold Wedding Ring",
                "slug": "classic-gold-wedding-ring"
            },
            "quantity": 1,
            "price": "299.99",
            "total_price": "299.99"
        }
    ],
    "notes": "Please handle with care",
    "created_at": "2024-01-01T10:00:00Z"
}
```

---

### 2. Get Orders

**Endpoint:** `GET /orders/`

**Description:** Get all your orders with filtering options

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `status`: Filter by order status (`pending`, `confirmed`, `processing`, `shipped`, `delivered`, `cancelled`, `refunded`)
- `payment_status`: Filter by payment status (`pending`, `paid`, `failed`, `refunded`)
- `date_from`: Filter orders from date (YYYY-MM-DD)
- `date_to`: Filter orders to date (YYYY-MM-DD)
- `page`: Page number
- `page_size`: Items per page

**Example Request:**
```
GET http://localhost:8000/orders/?status=delivered&page=1
```

**Response (200 OK):**
```json
{
    "count": 3,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "order_number": "ORD-20240101-001",
            "status": "delivered",
            "payment_status": "paid",
            "subtotal": "299.99",
            "tax_amount": "15.00",
            "shipping_cost": "10.00",
            "total_amount": "324.99",
            "shipping_address": {
                "first_name": "John",
                "last_name": "Doe",
                "address_line_1": "123 Main St",
                "city": "New York",
                "state": "NY",
                "postal_code": "10001",
                "country": "USA"
            },
            "billing_address": {
                "first_name": "John",
                "last_name": "Doe",
                "address_line_1": "123 Main St",
                "city": "New York",
                "state": "NY",
                "postal_code": "10001",
                "country": "USA"
            },
            "items": [
                {
                    "id": 1,
                    "product": {
                        "id": 1,
                        "title": "Classic Gold Wedding Ring",
                        "slug": "classic-gold-wedding-ring"
                    },
                    "quantity": 1,
                    "price": "299.99",
                    "total_price": "299.99"
                }
            ],
            "tracking_number": "TRK123456",
            "notes": "Please handle with care",
            "created_at": "2024-01-01T10:00:00Z",
            "shipped_at": "2024-01-02T10:00:00Z",
            "delivered_at": "2024-01-05T10:00:00Z"
        }
    ]
}
```

---

### 3. Get Order Details

**Endpoint:** `GET /orders/{id}/`

**Description:** Get detailed information about a specific order

**Headers:**
```
Authorization: Bearer <access_token>
```

**Example Request:**
```
GET http://localhost:8000/orders/1/
```

**Response (200 OK):**
```json
{
    "id": 1,
    "order_number": "ORD-20240101-001",
    "status": "delivered",
    "payment_status": "paid",
    "subtotal": "299.99",
    "tax_amount": "15.00",
    "shipping_cost": "10.00",
    "total_amount": "324.99",
    "shipping_address": {
        "first_name": "John",
        "last_name": "Doe",
        "address_line_1": "123 Main St",
        "city": "New York",
        "state": "NY",
        "postal_code": "10001",
        "country": "USA",
        "phone": "555-123-4567"
    },
    "billing_address": {
        "first_name": "John",
        "last_name": "Doe",
        "address_line_1": "123 Main St",
        "city": "New York",
        "state": "NY",
        "postal_code": "10001",
        "country": "USA",
        "phone": "555-123-4567"
    },
    "items": [
        {
            "id": 1,
            "product": {
                "id": 1,
                "title": "Classic Gold Wedding Ring",
                "slug": "classic-gold-wedding-ring",
                "price": "299.99",
                "images": [
                    {
                        "image": "/media/products/classic_gold_wedding_ring.jpg",
                        "alt_text": "Classic Gold Wedding Ring image",
                        "is_main": true
                    }
                ]
            },
            "quantity": 1,
            "price": "299.99",
            "total_price": "299.99"
        }
    ],
    "payments": [
        {
            "id": 1,
            "payment_method": "credit_card",
            "amount": "324.99",
            "status": "completed",
            "transaction_id": "TXN12345678",
            "created_at": "2024-01-01T10:00:00Z",
            "completed_at": "2024-01-01T10:05:00Z"
        }
    ],
    "tracking_number": "TRK123456",
    "notes": "Please handle with care",
    "created_at": "2024-01-01T10:00:00Z",
    "shipped_at": "2024-01-02T10:00:00Z",
    "delivered_at": "2024-01-05T10:00:00Z"
}
```

---

## Stripe Payments

This section covers how to process payments using Stripe integration. Stripe provides secure payment processing for credit cards, debit cards, and other payment methods.

### Payment Methods

We support two Stripe payment methods:

#### Option A: Stripe Checkout Sessions (Recommended - Simplest)
- Redirects users to Stripe's hosted payment page
- No frontend integration needed
- Stripe handles everything
- **Best for:** Quick setup, no custom payment form needed

#### Option B: Payment Intents with Stripe Elements
- Embed Stripe payment form in your own page
- Full control over payment UI
- Requires Stripe.js integration
- **Best for:** Custom payment page design

---

### Payment Flow Overview

#### Checkout Session Flow (Simplest)
1. **Create Order** → Create an order from cart
2. **Create Checkout Session** → Get Stripe payment page URL
3. **Redirect to Stripe** → User pays on Stripe's page
4. **Verify Payment** → After redirect back, verify payment status
5. **Webhook Updates** → Stripe automatically sends webhook events

#### Payment Intent Flow (Custom Form)
1. **Create Order** → Create an order from cart
2. **Get Stripe Config** → Get Stripe publishable key
3. **Create Payment Intent** → Create Stripe payment intent
4. **Confirm Payment (Frontend)** → Use Stripe.js to confirm payment
5. **Confirm Payment (Backend)** → Update payment status on backend
6. **Webhook Updates** → Stripe automatically sends webhook events

---

## Stripe Checkout Sessions (Simplest Method)

### 1. Create Checkout Session

**Endpoint:** `POST /payments/create-checkout-session/`

**Description:** Create a Stripe Checkout Session and get the URL to redirect users to Stripe's payment page. This is the simplest payment method - users pay on Stripe's hosted page.

**When to Call:** After creating an order (`POST /orders/create/`). This returns a URL that you redirect the user to for payment.

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request:**
```json
{
    "order_id": 1,
    "coupon_code": "SAVE10",
    "success_url": "https://yoursite.com/payment-success",
    "cancel_url": "https://yoursite.com/payment-cancelled"
}
```

**Request Parameters:**
- `order_id` (required): The ID of the order to create payment for
- `coupon_code` (optional): Coupon code to apply discount
- `success_url` (optional): URL to redirect after successful payment (default: `http://localhost:3000/payment-success`)
- `cancel_url` (optional): URL to redirect if user cancels (default: `http://localhost:3000/payment-cancelled`)

**Example Request:**
```bash
curl -X POST http://localhost:8000/payments/create-checkout-session/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": 1,
    "coupon_code": "SAVE10",
    "success_url": "https://yoursite.com/payment-success",
    "cancel_url": "https://yoursite.com/payment-cancelled"
  }'
```

**Response (200 OK):**
```json
{
    "checkout_url": "https://checkout.stripe.com/pay/cs_test_xxx",
    "session_id": "cs_test_xxx",
    "order_id": 1,
    "amount": 324.99
}
```

**Response Fields:**
- `checkout_url`: **Redirect user to this URL** - This is Stripe's payment page
- `session_id`: Stripe checkout session ID
- `order_id`: Your order ID
- `amount`: Final amount after coupon discount (if applied)

**Features:**
- Automatically creates line items from order items
- Applies coupon discount if valid coupon code provided
- Creates or updates Payment record
- Tracks coupon usage
- User pays on Stripe's secure payment page

**Frontend Usage:**
```javascript
// After creating order
const response = await fetch('/payments/create-checkout-session/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    order_id: orderId,
    success_url: window.location.origin + '/payment-success',
    cancel_url: window.location.origin + '/payment-cancelled'
  })
});

const { checkout_url } = await response.json();

// Redirect to Stripe payment page
window.location.href = checkout_url;
```

---

### 2. Verify Checkout Session

**Endpoint:** `POST /payments/verify-checkout/`

**Description:** Verify payment status after user returns from Stripe's payment page. Call this on your success page after redirect.

**When to Call:** After user is redirected back from Stripe (on your success page). Get `session_id` from URL parameter `?session_id=xxx`.

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request:**
```json
{
    "session_id": "cs_test_xxx",
    "order_id": 1
}
```

**Request Parameters:**
- `session_id` (required): The Stripe checkout session ID (from URL parameter `session_id`)
- `order_id` (optional): Order ID for verification

**Example Request:**
```bash
curl -X POST http://localhost:8000/payments/verify-checkout/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "cs_test_xxx",
    "order_id": 1
  }'
```

**Response (200 OK) - Payment Successful:**
```json
{
    "message": "Payment confirmed successfully",
    "payment": {
        "id": 1,
        "order": 1,
        "payment_method": "credit_card",
        "amount": "324.99",
        "status": "completed",
        "transaction_id": "cs_test_xxx",
        "created_at": "2024-01-01T10:00:00Z",
        "completed_at": "2024-01-01T10:05:00Z"
    },
    "order": {
        "id": 1,
        "order_number": "ORD-20240101-001",
        "status": "confirmed",
        "payment_status": "paid",
        ...
    },
    "payment_status": "paid"
}
```

**Response (200 OK) - Payment Pending:**
```json
{
    "message": "Payment is pending",
    "payment": {
        "id": 1,
        "status": "pending",
        ...
    },
    "payment_status": "pending"
}
```

**Frontend Usage (Success Page):**
```javascript
// On your payment-success page
const urlParams = new URLSearchParams(window.location.search);
const sessionId = urlParams.get('session_id');
const orderId = urlParams.get('order_id');

// Verify payment
const response = await fetch('/payments/verify-checkout/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    session_id: sessionId,
    order_id: orderId
  })
});

const result = await response.json();

if (result.payment_status === 'paid') {
  // Show success message
  console.log('Payment successful!', result);
} else {
  // Payment pending or failed
  console.log('Payment status:', result.payment_status);
}
```

---

## Payment Intents with Stripe Elements (Custom Form)

### 1. Get Stripe Configuration

**Endpoint:** `GET /payments/stripe-config/`

**Description:** Get Stripe publishable key needed to initialize Stripe.js on the frontend

**When to Call:** Before initializing Stripe on your payment page. Call this once when the payment page loads.

**Authentication:** Not required

**Example Request:**
```bash
curl -X GET http://localhost:8000/payments/stripe-config/
```

**Response (200 OK):**
```json
{
    "publishable_key": "pk_test_51SMo1w19sRzf7Gr7jPKMjilgZ6W2vMWAICMUCIoMzNp6as15s2O8FB1TzgQnTKO0lLYPLaN1rOnNAO9cow5fxoa300AMHh6NEp",
    "currency": "usd"
}
```

**Usage:**
```javascript
// Frontend example
const response = await fetch('/payments/stripe-config/');
const { publishable_key } = await response.json();
const stripe = Stripe(publishable_key);
```

---

### 2. Create Payment Intent

**Endpoint:** `POST /payments/create-intent/`

**Description:** Create a Stripe Payment Intent for an order. This must be called after creating an order and before showing the payment form.

**When to Call:** After creating an order (`POST /orders/create/`) and before displaying the payment form to the user.

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request:**
```json
{
    "order_id": 1,
    "coupon_code": "SAVE10"
}
```

**Request Parameters:**
- `order_id` (required): The ID of the order to create payment for
- `coupon_code` (optional): Coupon code to apply discount

**Example Request:**
```bash
curl -X POST http://localhost:8000/payments/create-intent/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": 1,
    "coupon_code": "SAVE10"
  }'
```

**Response (200 OK):**
```json
{
    "client_secret": "pi_xxx_secret_xxx",
    "payment_intent_id": "pi_xxx",
    "amount": 324.99,
    "currency": "usd",
    "payment_id": 1
}
```

**Response Fields:**
- `client_secret`: Use this with Stripe.js to confirm payment on frontend
- `payment_intent_id`: Stripe payment intent ID
- `amount`: Final amount after coupon discount (if applied)
- `currency`: Payment currency (always "usd")
- `payment_id`: Payment record ID in your system

**Features:**
- Automatically creates a Payment record
- Applies coupon discount if valid coupon code provided
- Returns existing payment intent if one already exists for the order
- Validates coupon and tracks usage

**Error Responses:**
- `400 Bad Request`: Invalid order ID or Stripe API error
- `404 Not Found`: Order not found
- `403 Forbidden`: Order doesn't belong to authenticated user

---

### 3. Confirm Payment

**Endpoint:** `POST /payments/confirm/`

**Description:** Confirm payment after successfully confirming payment on the frontend using Stripe.js. This updates the payment and order status on the backend.

**When to Call:** After `stripe.confirmCardPayment()` succeeds on the frontend. This verifies the payment status with Stripe and updates your database.

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request:**
```json
{
    "payment_intent_id": "pi_xxx",
    "order_id": 1
}
```

**Request Parameters:**
- `payment_intent_id` (required): The Stripe payment intent ID from frontend confirmation
- `order_id` (optional): Order ID for verification

**Example Request:**
```bash
curl -X POST http://localhost:8000/payments/confirm/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "payment_intent_id": "pi_xxx",
    "order_id": 1
  }'
```

**Response (200 OK) - Payment Succeeded:**
```json
{
    "message": "Payment confirmed successfully",
    "payment": {
        "id": 1,
        "order": 1,
        "payment_method": "credit_card",
        "amount": "324.99",
        "status": "completed",
        "transaction_id": "pi_xxx",
        "created_at": "2024-01-01T10:00:00Z",
        "completed_at": "2024-01-01T10:05:00Z"
    },
    "order": {
        "id": 1,
        "order_number": "ORD-20240101-001",
        "status": "confirmed",
        "payment_status": "paid",
        "total_amount": "324.99",
        ...
    }
}
```

**Response (200 OK) - Payment Processing:**
```json
{
    "message": "Payment is processing",
    "payment": {
        "id": 1,
        "status": "processing",
        ...
    }
}
```

**Response (400 Bad Request) - Payment Failed:**
```json
{
    "error": "Payment requires a payment method",
    "payment": {
        "id": 1,
        "status": "failed",
        ...
    }
}
```

**Payment Statuses:**
- `succeeded`: Payment completed successfully → Order status updated to "confirmed", payment status to "paid"
- `processing`: Payment is being processed → Payment status updated to "processing"
- `requires_payment_method`: Payment failed → Payment status updated to "failed"
- Other statuses: Payment failed → Payment status updated to "failed"

---

### 4. Stripe Webhook

**Endpoint:** `POST /payments/webhook/`

**Description:** Webhook endpoint that Stripe calls automatically when payment events occur. This is NOT called by your application - Stripe calls it directly.

**When to Call:** Never call this directly. Configure this URL in your Stripe Dashboard under Webhooks. Stripe will automatically send events here.

**Authentication:** Not required (uses Stripe signature verification)

**Headers (Set by Stripe):**
```
Stripe-Signature: t=xxx,v1=xxx
Content-Type: application/json
```

**Webhook Events Handled:**
- `checkout.session.completed`: Updates payment and order status to completed/paid (for Checkout Sessions)
- `payment_intent.succeeded`: Updates payment and order status to completed/paid (for Payment Intents)
- `payment_intent.payment_failed`: Updates payment and order status to failed

**Response:**
```json
{
    "status": "success"
}
```

**Configuration:**
1. Go to Stripe Dashboard → Developers → Webhooks
2. Click "Add endpoint"
3. Enter URL: `https://yourdomain.com/payments/webhook/`
4. Select events: 
   - `checkout.session.completed` (for Checkout Sessions)
   - `payment_intent.succeeded` (for Payment Intents)
   - `payment_intent.payment_failed` (for Payment Intents)
5. Copy the webhook signing secret and add to your settings

**Note:** For local development, use Stripe CLI:
```bash
stripe listen --forward-to localhost:8000/payments/webhook/
```

---

### 5. Get Payments

**Endpoint:** `GET /payments/`

**Description:** Get list of all payments for the authenticated user

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `status`: Filter by payment status (`pending`, `processing`, `completed`, `failed`, `cancelled`, `refunded`)
- `payment_method`: Filter by payment method (`credit_card`, `debit_card`, `paypal`, etc.)
- `date_from`: Filter payments from date (YYYY-MM-DD)
- `date_to`: Filter payments to date (YYYY-MM-DD)

**Example Request:**
```
GET http://localhost:8000/payments/?status=completed&payment_method=credit_card
```

**Response (200 OK):**
```json
[
    {
        "id": 1,
        "order": {
            "id": 1,
            "order_number": "ORD-20240101-001"
        },
        "payment_method": "credit_card",
        "amount": "324.99",
        "status": "completed",
        "transaction_id": "pi_xxx",
        "created_at": "2024-01-01T10:00:00Z",
        "completed_at": "2024-01-01T10:05:00Z"
    }
]
```

---

### 6. Get Payment Detail

**Endpoint:** `GET /payments/{id}/`

**Description:** Get detailed information about a specific payment

**Headers:**
```
Authorization: Bearer <access_token>
```

**Example Request:**
```
GET http://localhost:8000/payments/1/
```

**Response (200 OK):**
```json
{
    "id": 1,
    "order": {
        "id": 1,
        "order_number": "ORD-20240101-001",
        "status": "confirmed",
        "total_amount": "324.99"
    },
    "payment_method": "credit_card",
    "amount": "324.99",
    "status": "completed",
    "transaction_id": "pi_xxx",
    "gateway_response": {
        "payment_intent": {...},
        "status": "succeeded"
    },
    "created_at": "2024-01-01T10:00:00Z",
    "completed_at": "2024-01-01T10:05:00Z"
}
```

---

## Frontend Integration Examples

### Checkout Session Example (Simplest)

```javascript
// Step 1: Create order (from cart)
const orderResponse = await fetch('/orders/create/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    shipping_address: {...},
    billing_address: {...},
    notes: 'Please handle with care'
  })
});
const order = await orderResponse.json();

// Step 2: Create checkout session
const sessionResponse = await fetch('/payments/create-checkout-session/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    order_id: order.id,
    coupon_code: 'SAVE10', // Optional
    success_url: window.location.origin + '/payment-success',
    cancel_url: window.location.origin + '/payment-cancelled'
  })
});
const { checkout_url } = await sessionResponse.json();

// Step 3: Redirect to Stripe payment page
window.location.href = checkout_url;

// Step 4: On success page (after redirect)
const urlParams = new URLSearchParams(window.location.search);
const sessionId = urlParams.get('session_id');
const orderId = urlParams.get('order_id');

// Verify payment
const verifyResponse = await fetch('/payments/verify-checkout/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    session_id: sessionId,
    order_id: orderId
  })
});

const result = await verifyResponse.json();
if (result.payment_status === 'paid') {
  console.log('Payment successful!', result);
}
```

### Payment Intent Example (Custom Form)

```javascript
// Step 1: Get Stripe config
const configResponse = await fetch('/payments/stripe-config/');
const { publishable_key } = await configResponse.json();
const stripe = Stripe(publishable_key);

// Step 2: Create order (from cart)
const orderResponse = await fetch('/orders/create/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    shipping_address: {...},
    billing_address: {...},
    notes: 'Please handle with care'
  })
});
const order = await orderResponse.json();

// Step 3: Create payment intent
const intentResponse = await fetch('/payments/create-intent/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    order_id: order.id,
    coupon_code: couponCode // Optional
  })
});
const { client_secret, payment_intent_id } = await intentResponse.json();

// Step 4: Confirm payment with Stripe.js
const { error, paymentIntent } = await stripe.confirmCardPayment(
  client_secret,
  {
    payment_method: {
      card: cardElement,
      billing_details: {
        name: 'Customer Name',
        email: 'customer@example.com',
      },
    },
  }
);

if (error) {
  // Handle error
  console.error('Payment failed:', error);
} else if (paymentIntent.status === 'succeeded') {
  // Step 5: Confirm payment on backend
  const confirmResponse = await fetch('/payments/confirm/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      payment_intent_id: paymentIntent.id,
      order_id: order.id
    })
  });
  
  const result = await confirmResponse.json();
  console.log('Payment confirmed:', result);
  // Redirect to success page
}
```

---

## Complete Payment Flow

### Checkout Session Flow (Simplest)

1. **User adds items to cart** → `POST /cart/`
2. **User views cart** → `GET /cart/`
3. **User creates order** → `POST /orders/create/`
4. **Create checkout session** → `POST /payments/create-checkout-session/` (with order_id)
5. **Redirect to Stripe** → User pays on Stripe's payment page
6. **User redirected back** → To your success/cancel URL
7. **Verify payment** → `POST /payments/verify-checkout/` (on success page)
8. **Webhook updates** → Stripe automatically sends webhook events
9. **View payment status** → `GET /payments/` or `GET /payments/{id}/`

### Payment Intent Flow (Custom Form)

1. **User adds items to cart** → `POST /cart/`
2. **User views cart** → `GET /cart/`
3. **User creates order** → `POST /orders/create/`
4. **Get Stripe config** → `GET /payments/stripe-config/` (once, when payment page loads)
5. **Create payment intent** → `POST /payments/create-intent/` (with order_id)
6. **Frontend confirms payment** → Using Stripe.js with `client_secret`
7. **Confirm payment on backend** → `POST /payments/confirm/` (after frontend confirmation)
8. **Webhook updates** → Stripe automatically sends webhook events
9. **View payment status** → `GET /payments/` or `GET /payments/{id}/`

---

## Payment Status Flow

```
Order Created (payment_status: pending)
    ↓
Payment Intent Created (payment status: pending)
    ↓
Frontend Confirms Payment
    ↓
Backend Confirms Payment
    ↓
Payment Status: completed → Order Status: confirmed, payment_status: paid
```

If payment fails:
```
Payment Status: failed → Order payment_status: failed
```

---

## Error Handling

### Common Payment Errors

**400 Bad Request:**
```json
{
    "error": "Invalid order ID"
}
```

**404 Not Found:**
```json
{
    "error": "Order not found"
}
```

**403 Forbidden:**
```json
{
    "error": "Unauthorized"
}
```

### Stripe Error Handling

When `stripe.confirmCardPayment()` fails, handle errors:

```javascript
const { error, paymentIntent } = await stripe.confirmCardPayment(client_secret, {...});

if (error) {
  switch (error.type) {
    case 'card_error':
      // Card was declined
      console.error('Card error:', error.message);
      break;
    case 'validation_error':
      // Invalid input
      console.error('Validation error:', error.message);
      break;
    default:
      // Other error
      console.error('Error:', error.message);
  }
}
```

---

## Testing

### Test Cards

Use these test card numbers in Stripe test mode:

- **Success:** `4242 4242 4242 4242`
- **Requires Authentication:** `4000 0025 0000 3155`
- **Declined:** `4000 0000 0000 0002`

Use any:
- Future expiry date (e.g., 12/25)
- Any 3-digit CVC (e.g., 123)
- Any ZIP code (e.g., 12345)

### Testing Flow

1. Create a test order
2. Use test card `4242 4242 4242 4242`
3. Complete payment flow
4. Check payment status via `GET /payments/`
5. Verify order status updated to "confirmed" and "paid"

---

## Security Notes

1. **Never expose secret keys** in frontend code
2. **Always verify payment status** on backend after frontend confirmation
3. **Use HTTPS** in production
4. **Verify webhook signatures** (handled automatically)
5. **Store sensitive keys** in environment variables

---

## Managing Your Account

### 1. Get User Profile

**Endpoint:** `GET /auth/profile/`

**Description:** Get your profile information

**Headers:**
```
Authorization: Bearer <access_token>
```

**Example Request:**
```bash
curl -X GET http://localhost:8000/auth/profile/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response (200 OK):**
```json
{
    "user": {
        "id": 1,
        "loginname": "john_doe",
        "email": "john.doe@example.com",
        "first_name": "John",
        "last_name": "Doe"
    },
    "phone": "555-123-4567",
    "date_of_birth": "1990-01-01",
    "gender": "male",
    "bio": "Jewelry enthusiast",
    "newsletter_subscription": true,
    "email_notifications": true,
    "instagram": "@john_jewels"
}
```

---

### 2. Update User Profile

**Endpoint:** `PUT /auth/profile/`

**Description:** Update your profile information

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request:**
```json
{
    "phone": "555-123-4567",
    "date_of_birth": "1990-01-01",
    "gender": "male",
    "bio": "Updated bio",
    "newsletter_subscription": true,
    "email_notifications": true,
    "instagram": "@john_jewels"
}
```

**Example Request:**
```bash
curl -X PUT http://localhost:8000/auth/profile/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "555-123-4567",
    "date_of_birth": "1990-01-01",
    "gender": "male",
    "bio": "Updated bio",
    "newsletter_subscription": true,
    "email_notifications": true,
    "instagram": "@john_jewels"
  }'
```

---

### 3. Get Extended Profile

**Endpoint:** `GET /auth/profile/extended/`

**Description:** Get complete profile with addresses

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
    "user": {
        "id": 1,
        "loginname": "john_doe",
        "email": "john.doe@example.com",
        "first_name": "John",
        "last_name": "Doe"
    },
    "profile": {
        "phone": "555-123-4567",
        "date_of_birth": "1990-01-01",
        "gender": "male",
        "bio": "Jewelry enthusiast",
        "newsletter_subscription": true,
        "email_notifications": true,
        "instagram": "@john_jewels"
    },
    "addresses": [
        {
            "id": 1,
            "address_type": "home",
            "first_name": "John",
            "last_name": "Doe",
            "address_line_1": "123 Main St",
            "city": "New York",
            "state": "NY",
            "postal_code": "10001",
            "country": "USA",
            "phone": "555-123-4567",
            "is_default": true,
            "is_shipping": true,
            "is_billing": true
        }
    ]
}
```

---

### 4. Get Addresses

**Endpoint:** `GET /auth/addresses/`

**Description:** Get all your saved addresses

**Headers:**
```
Authorization: Bearer <access_token>
```

**Example Request:**
```bash
curl -X GET http://localhost:8000/auth/addresses/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response (200 OK):**
```json
[
    {
        "id": 1,
        "address_type": "home",
        "first_name": "John",
        "last_name": "Doe",
        "company": "",
        "address_line_1": "123 Main St",
        "address_line_2": "",
        "city": "New York",
        "state": "NY",
        "postal_code": "10001",
        "country": "USA",
        "phone": "555-123-4567",
        "is_default": true,
        "is_shipping": true,
        "is_billing": true
    }
]
```

---

### 5. Create Address

**Endpoint:** `POST /auth/addresses/`

**Description:** Add a new address

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request:**
```json
{
    "address_type": "work",
    "first_name": "John",
    "last_name": "Doe",
    "company": "Tech Corp",
    "address_line_1": "456 Business Ave",
    "city": "New York",
    "state": "NY",
    "postal_code": "10002",
    "country": "USA",
    "phone": "555-987-6543",
    "is_default": false,
    "is_shipping": true,
    "is_billing": false
}
```

**Example Request:**
```bash
curl -X POST http://localhost:8000/auth/addresses/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "address_type": "work",
    "first_name": "John",
    "last_name": "Doe",
    "company": "Tech Corp",
    "address_line_1": "456 Business Ave",
    "city": "New York",
    "state": "NY",
    "postal_code": "10002",
    "country": "USA",
    "phone": "555-987-6543",
    "is_default": false,
    "is_shipping": true,
    "is_billing": false
  }'
```

---

### 6. Update Address

**Endpoint:** `PUT /auth/addresses/{id}/`

**Description:** Update an existing address

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request:**
```json
{
    "address_type": "home",
    "first_name": "John",
    "last_name": "Doe",
    "address_line_1": "789 Updated St",
    "city": "New York",
    "state": "NY",
    "postal_code": "10003",
    "country": "USA",
    "phone": "555-111-2222",
    "is_default": true,
    "is_shipping": true,
    "is_billing": true
}
```

---

### 7. Delete Address

**Endpoint:** `DELETE /auth/addresses/{id}/`

**Description:** Delete an address

**Headers:**
```
Authorization: Bearer <access_token>
```

**Example Request:**
```bash
curl -X DELETE http://localhost:8000/auth/addresses/1/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response (204 No Content):**
```
No content
```

---

## Product Reviews

### 1. Get Product Reviews

**Endpoint:** `GET /products/{slug}/reviews/`

**Description:** Get all reviews for a specific product

**Example Request:**
```
GET http://localhost:8000/products/classic-gold-wedding-ring/reviews/
```

**Response (200 OK):**
```json
[
    {
        "id": 1,
        "user": {
            "id": 1,
            "loginname": "john_doe",
            "first_name": "John",
            "last_name": "Doe"
        },
        "rating": 5,
        "comment": "Absolutely love this piece! Highly recommend.",
        "status": 1,
        "created_at": "2024-01-01T10:00:00Z"
    }
]
```

---

### 2. Create Product Review

**Endpoint:** `POST /products/{slug}/reviews/`

**Description:** Create a review for a product

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request:**
```json
{
    "rating": 5,
    "comment": "Excellent product! Very satisfied with the quality."
}
```

**Example Request:**
```bash
curl -X POST http://localhost:8000/products/classic-gold-wedding-ring/reviews/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "rating": 5,
    "comment": "Excellent product! Very satisfied with the quality."
  }'
```

**Response (201 Created):**
```json
{
    "id": 2,
    "user": {
        "id": 1,
        "loginname": "john_doe",
        "first_name": "John",
        "last_name": "Doe"
    },
    "rating": 5,
    "comment": "Excellent product! Very satisfied with the quality.",
    "status": 2,
    "created_at": "2024-01-01T10:00:00Z"
}
```

---

### 3. Get Review Detail

**Endpoint:** `GET /reviews/{id}/`

**Description:** Get specific review details

**Example Request:**
```
GET http://localhost:8000/reviews/1/
```

**Response (200 OK):**
```json
{
    "id": 1,
    "user": {
        "id": 1,
        "loginname": "john_doe",
        "first_name": "John",
        "last_name": "Doe"
    },
    "product": {
        "id": 1,
        "title": "Classic Gold Wedding Ring",
        "slug": "classic-gold-wedding-ring"
    },
    "rating": 5,
    "comment": "Absolutely love this piece! Highly recommend.",
    "status": 1,
    "created_at": "2024-01-01T10:00:00Z"
}
```

---

### 4. Update Review

**Endpoint:** `PUT /reviews/{id}/`

**Description:** Update your review (only the review owner can update)

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request:**
```json
{
    "rating": 4,
    "comment": "Updated review comment"
}
```

**Example Request:**
```bash
curl -X PUT http://localhost:8000/reviews/1/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "rating": 4,
    "comment": "Updated review comment"
  }'
```

---

### 5. Delete Review

**Endpoint:** `DELETE /reviews/{id}/`

**Description:** Delete your review (only the review owner can delete)

**Headers:**
```
Authorization: Bearer <access_token>
```

**Example Request:**
```bash
curl -X DELETE http://localhost:8000/reviews/1/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response (204 No Content):**
```
No content
```

---

## Search & Filters

### 1. Search Products

**Endpoint:** `GET /search/`

**Description:** Search products with advanced filtering

**Query Parameters:**
- `q`: Search query (required)
- `category`: Filter by category
- `material`: Filter by material
- `gemstone`: Filter by gemstone
- `min_price`: Minimum price
- `max_price`: Maximum price
- `jewelry_type`: Filter by jewelry type
- `ordering`: Sort order

**Example Request:**
```
GET http://localhost:8000/search/?q=gold ring&category=rings&min_price=100&max_price=500&ordering=-price
```

**Response (200 OK):**
```json
{
    "query": "gold ring",
    "count": 2,
    "results": [
        {
            "id": 1,
            "title": "Classic Gold Wedding Ring",
            "slug": "classic-gold-wedding-ring",
            "price": "299.99",
            "images": [
                {
                    "image": "/media/products/classic_gold_wedding_ring.jpg",
                    "alt_text": "Classic Gold Wedding Ring image",
                    "is_main": true
                }
            ],
            "average_rating": 4.5,
            "review_count": 3
        }
    ]
}
```

---

## Coupons & Discounts

### 1. Get Available Coupons

**Endpoint:** `GET /coupons/`

**Description:** Get list of all available coupons

**Example Request:**
```
GET http://localhost:8000/coupons/
```

**Response (200 OK):**
```json
[
    {
        "id": 1,
        "code": "SAVE10",
        "description": "10% off all orders",
        "discount_type": "percentage",
        "discount_value": "10.00",
        "minimum_order_amount": "50.00",
        "maximum_discount": null,
        "usage_limit": 100,
        "used_count": 5,
        "valid_from": "2024-01-01T00:00:00Z",
        "valid_until": "2024-12-31T23:59:59Z",
        "is_active": true,
        "created_at": "2024-01-01T10:00:00Z"
    }
]
```

---

### 2. Validate Coupon

**Endpoint:** `POST /coupons/validate/`

**Description:** Validate a coupon code before applying

**Request:**
```json
{
    "code": "SAVE10",
    "order_amount": "100.00"
}
```

**Example Request:**
```bash
curl -X POST http://localhost:8000/coupons/validate/ \
  -H "Content-Type: application/json" \
  -d '{
    "code": "SAVE10",
    "order_amount": "100.00"
  }'
```

**Response (200 OK):**
```json
{
    "valid": true,
    "discount_amount": "10.00",
    "message": "Coupon applied successfully"
}
```

**Error Response (400 Bad Request):**
```json
{
    "valid": false,
    "message": "Coupon not found or expired"
}
```

---

### 3. Get Coupon Usage History

**Endpoint:** `GET /coupons/usage/`

**Description:** Get your coupon usage history

**Headers:**
```
Authorization: Bearer <access_token>
```

**Example Request:**
```bash
curl -X GET http://localhost:8000/coupons/usage/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response (200 OK):**
```json
[
    {
        "id": 1,
        "coupon": {
            "id": 1,
            "code": "SAVE10",
            "description": "10% off all orders"
        },
        "order": {
            "id": 1,
            "order_number": "ORD-20240101-001"
        },
        "discount_amount": "10.00",
        "used_at": "2024-01-01T10:00:00Z"
    }
]
```

---

## Error Handling

### Common Error Responses

**400 Bad Request:**
```json
{
    "field_name": ["This field is required."],
    "another_field": ["Invalid value."]
}
```

**401 Unauthorized:**
```json
{
    "detail": "Authentication credentials were not provided."
}
```

**403 Forbidden:**
```json
{
    "detail": "You do not have permission to perform this action."
}
```

**404 Not Found:**
```json
{
    "error": "Resource not found"
}
```

**500 Internal Server Error:**
```json
{
    "detail": "A server error occurred."
}
```

---

## Complete Shopping Flow Example

Here's a complete example of the shopping flow:

### Step 1: Register
```bash
POST /auth/register/
{
    "loginname": "john_doe",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "password": "securepassword123"
}
```

### Step 2: Verify Email
```
GET /auth/verify-email/?uid=1&token=abc123
```

### Step 3: Login
```bash
POST /auth/login/
{
    "username": "john_doe",
    "password": "securepassword123"
}
# Save the access token!
```

### Step 4: Browse Products
```
GET /products/?category=rings&min_price=100&max_price=500
```

### Step 5: View Product Details
```
GET /products/classic-gold-wedding-ring/
```

### Step 6: Add to Cart
```bash
POST /cart/
Authorization: Bearer <access_token>
{
    "product": 1,
    "quantity": 2
}
```

### Step 7: View Cart
```bash
GET /cart/
Authorization: Bearer <access_token>
```

### Step 8: Validate Coupon (Optional)
```bash
POST /coupons/validate/
{
    "code": "SAVE10",
    "order_amount": "599.98"
}
```

### Step 9: Create Order
```bash
POST /orders/create/
Authorization: Bearer <access_token>
{
    "shipping_address": {
        "first_name": "John",
        "last_name": "Doe",
        "address_line_1": "123 Main St",
        "city": "New York",
        "state": "NY",
        "postal_code": "10001",
        "country": "USA",
        "phone": "555-123-4567"
    },
    "billing_address": {
        "first_name": "John",
        "last_name": "Doe",
        "address_line_1": "123 Main St",
        "city": "New York",
        "state": "NY",
        "postal_code": "10001",
        "country": "USA",
        "phone": "555-123-4567"
    },
    "notes": "Please handle with care"
}
```

### Step 10A: Create Checkout Session (Simplest Method)
```bash
POST /payments/create-checkout-session/
Authorization: Bearer <access_token>
{
    "order_id": 1,
    "coupon_code": "SAVE10",
    "success_url": "https://yoursite.com/payment-success",
    "cancel_url": "https://yoursite.com/payment-cancelled"
}
# Returns checkout_url - redirect user to this URL
```

### Step 11A: User Pays on Stripe's Page
```
User is redirected to Stripe's payment page
User enters card details and pays
User is redirected back to your success_url
```

### Step 12A: Verify Checkout Session
```bash
POST /payments/verify-checkout/
Authorization: Bearer <access_token>
{
    "session_id": "cs_test_xxx",
    "order_id": 1
}
# Verify payment after user returns from Stripe
```

### OR

### Step 10B: Get Stripe Config (Custom Form Method)
```bash
GET /payments/stripe-config/
# Returns publishable_key for Stripe.js initialization
```

### Step 11B: Create Payment Intent
```bash
POST /payments/create-intent/
Authorization: Bearer <access_token>
{
    "order_id": 1,
    "coupon_code": "SAVE10"
}
# Returns client_secret for Stripe.js confirmation
```

### Step 12B: Confirm Payment (Frontend)
```javascript
// Using Stripe.js (not an API call)
const { error, paymentIntent } = await stripe.confirmCardPayment(
  client_secret,
  {
    payment_method: {
      card: cardElement,
      billing_details: {
        name: 'John Doe',
        email: 'john.doe@example.com',
      },
    },
  }
);
```

### Step 13B: Confirm Payment (Backend)
```bash
POST /payments/confirm/
Authorization: Bearer <access_token>
{
    "payment_intent_id": "pi_xxx",
    "order_id": 1
}
# Updates payment and order status
```

### Step 14: Track Order
```bash
GET /orders/1/
Authorization: Bearer <access_token>
```

### Step 15: View Payment Status
```bash
GET /payments/1/
Authorization: Bearer <access_token>
```

### Step 16: Write Review
```bash
POST /products/classic-gold-wedding-ring/reviews/
Authorization: Bearer <access_token>
{
    "rating": 5,
    "comment": "Excellent product!"
}
```

---

## Tips for API Integration

1. **Always Include Authorization Header**: For authenticated endpoints, always include `Authorization: Bearer <access_token>`

2. **Handle Token Expiration**: Access tokens expire. Implement token refresh logic or re-authenticate when needed

3. **Use Pagination**: For list endpoints, use pagination parameters (`page`, `page_size`) to avoid loading too much data

4. **Error Handling**: Always check response status codes and handle errors appropriately

5. **Validate Input**: Validate user input before sending requests to avoid errors

6. **Rate Limiting**: Be aware of rate limits and implement appropriate retry logic

7. **Cache When Possible**: Cache product listings and categories to reduce API calls

8. **Use Filters**: Use query parameters to filter results on the server side rather than filtering client-side

---

## Support

For API support and questions:
- Check the full API documentation: `API_DOCUMENTATION.md`
- Contact the development team
- Review error responses for troubleshooting

---

*Last Updated: [Current Date]*
*Version: 1.0*
