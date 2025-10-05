# Jewelry E-commerce API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication
This API uses JWT (JSON Web Token) authentication. Include the access token in the Authorization header:
```
Authorization: Bearer <access_token>
```

## Table of Contents
1. [Authentication APIs](#authentication-apis)
2. [User Management APIs](#user-management-apis)
3. [Product APIs](#product-apis)
4. [Order APIs](#order-apis)
5. [Shopping Cart APIs](#shopping-cart-apis)
6. [Wishlist APIs](#wishlist-apis)
7. [Search APIs](#search-apis)

---

## Authentication APIs

### 1. User Login
**POST** `/auth/login/`

**Description:** Authenticate user and get JWT tokens

**Request Body:**
```json
{
    "username": "john_doe",
    "password": "password123"
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

**Error Responses:**
- `400 Bad Request`: Missing username or password
- `401 Unauthorized`: Invalid credentials
- `403 Forbidden`: User is inactive

---

### 2. User Logout
**POST** `/auth/logout/`

**Description:** Logout user and blacklist refresh token

**Request Body:**
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

### 3. User Registration
**POST** `/auth/register/`

**Description:** Register a new user account

**Request Body:**
```json
{
    "loginname": "new_user",
    "first_name": "New",
    "last_name": "User",
    "email": "new.user@example.com",
    "password": "securepassword123"
}
```

**Response (201 Created):**
```json
{
    "detail": "User created. Check your email to verify."
}
```

**Error Response (400 Bad Request):**
```json
{
    "loginname": ["This field is required."],
    "email": ["Enter a valid email address."]
}
```

---

### 4. Email Verification
**GET** `/auth/verify-email/?uid=1&token=abc123`

**Description:** Verify user email address

**Query Parameters:**
- `uid`: User ID
- `token`: Verification token

**Response (200 OK):**
```json
{
    "detail": "Email verified successfully."
}
```

---

## User Management APIs

### 5. Get User List
**GET** `/auth/users/`

**Description:** Get list of all users (Admin only)

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)

**Response (200 OK):**
```json
{
    "count": 5,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "loginname": "john_doe",
            "email": "john.doe@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "status": 1
        }
    ]
}
```

---

### 6. Get User Detail
**GET** `/auth/users/{id}/`

**Description:** Get specific user details

**Response (200 OK):**
```json
{
    "id": 1,
    "loginname": "john_doe",
    "email": "john.doe@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "status": 1,
    "created_at": "2024-01-01T10:00:00Z",
    "updated_at": "2024-01-01T10:00:00Z",
    "last_login": "2024-01-01T10:00:00Z",
    "is_staff": false,
    "is_superuser": false
}
```

---

### 7. Get User Profile
**GET** `/auth/profile/`

**Description:** Get current user's profile

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

### 8. Update User Profile
**PUT** `/auth/profile/`

**Description:** Update current user's profile

**Request Body:**
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

---

### 9. Get Extended User Profile
**GET** `/auth/profile/extended/`

**Description:** Get complete user profile with addresses

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

## Address APIs

### 10. Get Address List
**GET** `/auth/addresses/`

**Description:** Get user's addresses

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

### 11. Create Address
**POST** `/auth/addresses/`

**Description:** Create new address

**Request Body:**
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

---

### 12. Get Address Detail
**GET** `/auth/addresses/{id}/`

**Description:** Get specific address

**Response (200 OK):**
```json
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
```

---

### 13. Update Address
**PUT** `/auth/addresses/{id}/`

**Description:** Update address

**Request Body:**
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

### 14. Delete Address
**DELETE** `/auth/addresses/{id}/`

**Description:** Delete address

**Response (204 No Content):**
```
No content
```

---

## Product APIs

### 15. Get Categories
**GET** `/categories/`

**Description:** Get list of product categories

**Query Parameters:**
- `parent`: Filter by parent category name
- `search`: Search in category name and description

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

### 16. Create Category
**POST** `/categories/`

**Description:** Create new category (Admin only)

**Request Body:**
```json
{
    "name": "New Category",
    "description": "Category description",
    "parent": 1
}
```

---

### 17. Get Category Detail
**GET** `/categories/{slug}/`

**Description:** Get specific category

**Response (200 OK):**
```json
{
    "id": 1,
    "name": "Rings",
    "slug": "rings",
    "description": "Beautiful rings for every occasion",
    "parent": null,
    "created_at": "2024-01-01T10:00:00Z"
}
```

---

### 18. Update Category
**PUT** `/categories/{slug}/`

**Description:** Update category (Admin only)

**Request Body:**
```json
{
    "name": "Updated Rings",
    "description": "Updated description",
    "parent": null
}
```

---

### 19. Delete Category
**DELETE** `/categories/{slug}/`

**Description:** Delete category (Admin only)

**Response (204 No Content):**
```
No content
```

---

### 20. Get Products
**GET** `/products/`

**Description:** Get list of products

**Query Parameters:**
- `category`: Filter by category slug
- `material`: Filter by material name
- `gemstone`: Filter by gemstone name
- `min_price`: Minimum price filter
- `max_price`: Maximum price filter
- `jewelry_type`: Filter by jewelry type (ring, necklace, earring, bracelet)
- `is_featured`: Filter featured products (true/false)
- `is_customizable`: Filter customizable products (true/false)
- `search`: Search in product title and description
- `ordering`: Sort by field (price, -price, created_at, -created_at)
- `page`: Page number
- `page_size`: Items per page

**Response (200 OK):**
```json
{
    "count": 8,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "title": "Classic Gold Wedding Ring",
            "slug": "classic-gold-wedding-ring",
            "description": "A timeless 18K gold wedding band.",
            "price": "299.99",
            "cost_price": "150.00",
            "markup_percentage": "100.00",
            "stock_quantity": 50,
            "is_featured": true,
            "jewelry_type": "ring",
            "weight": "3.5",
            "dimensions": "2mm band width",
            "is_customizable": false,
            "care_instructions": "Clean with soft cloth.",
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
            "average_rating": 4.5,
            "review_count": 3,
            "created_at": "2024-01-01T10:00:00Z"
        }
    ]
}
```

---

### 21. Create Product
**POST** `/products/create/`

**Description:** Create new product (Admin only)

**Request Body:**
```json
{
    "title": "New Product",
    "description": "Product description",
    "price": "199.99",
    "cost_price": "100.00",
    "markup_percentage": "99.99",
    "stock_quantity": 25,
    "is_featured": false,
    "jewelry_type": "ring",
    "weight": "2.5",
    "dimensions": "1cm diameter",
    "is_customizable": true,
    "customization_options": {
        "size": ["4-10"],
        "metal": ["gold", "silver"]
    },
    "care_instructions": "Handle with care",
    "category": 1,
    "primary_material": 1,
    "secondary_materials": [2, 3]
}
```

---

### 22. Get Product Detail
**GET** `/products/{slug}/`

**Description:** Get specific product details

**Response (200 OK):**
```json
{
    "id": 1,
    "title": "Classic Gold Wedding Ring",
    "slug": "classic-gold-wedding-ring",
    "description": "A timeless 18K gold wedding band.",
    "studio_notes": "Hand-polished finish.",
    "price": "299.99",
    "cost_price": "150.00",
    "markup_percentage": "100.00",
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

### 23. Update Product
**PUT** `/products/{slug}/update/`

**Description:** Update product (Admin only)

**Request Body:**
```json
{
    "title": "Updated Product Title",
    "description": "Updated description",
    "price": "249.99",
    "stock_quantity": 30,
    "is_featured": true
}
```

---

### 24. Delete Product
**DELETE** `/products/{slug}/delete/`

**Description:** Delete product (Admin only)

**Response (204 No Content):**
```
No content
```

---

### 25. Get Featured Products
**GET** `/products/featured/`

**Description:** Get featured products

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

### 26. Get Related Products
**GET** `/products/{slug}/related/`

**Description:** Get products related to the specified product

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

### 27. Get Product Reviews
**GET** `/products/{slug}/reviews/`

**Description:** Get reviews for a specific product

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

### 28. Create Product Review
**POST** `/products/{slug}/reviews/`

**Description:** Create a review for a product

**Request Body:**
```json
{
    "rating": 5,
    "comment": "Excellent product!"
}
```

---

### 29. Get Review Detail
**GET** `/reviews/{id}/`

**Description:** Get specific review

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

### 30. Update Review
**PUT** `/reviews/{id}/`

**Description:** Update review (Owner only)

**Request Body:**
```json
{
    "rating": 4,
    "comment": "Updated review comment"
}
```

---

### 31. Delete Review
**DELETE** `/reviews/{id}/`

**Description:** Delete review (Owner only)

**Response (204 No Content):**
```
No content
```

---

### 32. Get Products by Category
**GET** `/get-products/`

**Description:** Get products by category with specified count

**Query Parameters:**
- `category`: Category slug (required)
- `count`: Number of products to return (optional, default: 4)

**Example Requests:**
```
GET /get-products/?category=bride-groom-collection&count=4
GET /get-products/?category=rings&count=8
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
    },
    {
        "id": 3,
        "name": "Pearl Drop Earrings",
        "slug": "pearl-drop-earrings",
        "price": "89.99",
        "image": "/media/products/pearl_drop_earrings.jpg"
    },
    {
        "id": 4,
        "name": "Silver Bracelet",
        "slug": "silver-bracelet",
        "price": "149.99",
        "image": "/media/products/silver_bracelet.jpg"
    }
]
```

**Error Responses:**
- `400 Bad Request`: Missing category parameter or invalid count
- `404 Not Found`: Category not found

---

## Product Image APIs

### 33. Get Product Images
**GET** `/products/{slug}/images/`

**Description:** Get all images for a specific product

**Response (200 OK):**
```json
[
    {
        "id": 1,
        "image": "/media/products/classic_gold_wedding_ring.jpg",
        "alt_text": "Classic Gold Wedding Ring image",
        "is_main": true,
        "order": 1
    },
    {
        "id": 2,
        "image": "/media/products/classic_gold_wedding_ring_side.jpg",
        "alt_text": "Classic Gold Wedding Ring side view",
        "is_main": false,
        "order": 2
    }
]
```

---

### 34. Upload Product Image
**POST** `/products/{slug}/images/upload/`

**Description:** Upload a new image for a product (Admin only)

**Content-Type:** `multipart/form-data`

**Request Body (Form Data):**
- `image`: Image file (required)
- `alt_text`: Alt text for the image (optional)
- `is_main`: Set as main image (optional, boolean)

**Response (201 Created):**
```json
{
    "id": 3,
    "image": "/media/products/classic_gold_wedding_ring_detail.jpg",
    "alt_text": "Classic Gold Wedding Ring detail view",
    "is_main": false,
    "order": 3
}
```

**Error Responses:**
- `400 Bad Request`: No image file provided
- `404 Not Found`: Product not found
- `403 Forbidden`: Admin access required

---

### 35. Get Product Image Detail
**GET** `/products/{slug}/images/{id}/`

**Description:** Get specific product image details (Admin only)

**Response (200 OK):**
```json
{
    "id": 1,
    "image": "/media/products/classic_gold_wedding_ring.jpg",
    "alt_text": "Classic Gold Wedding Ring image",
    "is_main": true,
    "order": 1
}
```

---

### 36. Update Product Image
**PUT** `/products/{slug}/images/{id}/`

**Description:**### 36. Update Product Image details (Admin only)

**Request Body:**
```json
{
    "alt_text": "Updated alt text",
    "is_main": false,
    "order": 2
}
```

**Response (200 OK):**
```json
{
    "id": 1,
    "image": "/media/products/classic_gold_wedding_ring.jpg",
    "alt_text": "Updated alt text",
    "is_main": false,
    "order": 2
}
```

---

### 37. Delete Product Image
**DELETE** `/products/{slug}/images/{id}/`

**Description:**### 37. Delete Product Image (Admin only)

**Response (204 No Content):**
```
No content
```

---

### 38. Set Main Product Image
**POST** `/products/{slug}/images/{id}/set-main/`

**Description:** Set a specific image as the main image for a product (Admin only)

**Response (200 OK):**
```json
{
    "id": 2,
    "image": "/media/products/classic_gold_wedding_ring_side.jpg",
    "alt_text": "Classic Gold Wedding Ring side view",
    "is_main": true,
    "order": 2
}
```

---

### 39. Reorder Product Images
**POST** `/products/{slug}/images/reorder/`

**Description:**### 39. Reorder Product Images (Admin only)

**Request Body:**
```json
{
    "image_orders": [
        {
            "image_id": 1,
            "order": 2
        },
        {
            "image_id": 2,
            "order": 1
        },
        {
            "image_id": 3,
            "order": 3
        }
    ]
}
```

**Response (200 OK):**
```json
[
    {
        "id": 2,
        "image": "/media/products/classic_gold_wedding_ring_side.jpg",
        "alt_text": "Classic Gold Wedding Ring side view",
        "is_main": true,
        "order": 1
    },
    {
        "id": 1,
        "image": "/media/products/classic_gold_wedding_ring.jpg",
        "alt_text": "Classic Gold Wedding Ring image",
        "is_main": false,
        "order": 2
    },
    {
        "id": 3,
        "image": "/media/products/classic_gold_wedding_ring_detail.jpg",
        "alt_text": "Classic Gold Wedding Ring detail view",
        "is_main": false,
        "order": 3
    }
]
```

---

### 40. Get Materials
**GET** `/materials/`

**Description:** Get list of materials

**Response (200 OK):**
```json
[
    {
        "id": 1,
        "name": "Gold",
        "is_precious": true,
        "description": "24K, 18K, 14K Gold",
        "created_at": "2024-01-01T10:00:00Z"
    },
    {
        "id": 2,
        "name": "Silver",
        "is_precious": true,
        "description": "Pure Silver",
        "created_at": "2024-01-01T10:00:00Z"
    }
]
```

---

### 41. Get Gemstones
**GET** `/gemstones/`

**Description:** Get list of gemstones

**Response (200 OK):**
```json
[
    {
        "id": 1,
        "name": "Diamond",
        "color": "Clear",
        "hardness": "10.0",
        "description": "The hardest natural substance",
        "created_at": "2024-01-01T10:00:00Z"
    },
    {
        "id": 2,
        "name": "Ruby",
        "color": "Red",
        "hardness": "9.0",
        "description": "Precious red gemstone",
        "created_at": "2024-01-01T10:00:00Z"
    }
]
```

---

## Shopping Cart APIs

### 42. Get Cart
**GET** `/cart/`

**Description:** Get user's shopping cart

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

### 43. Add Item to Cart
**POST** `/cart/`

**Description:** Add product to cart

**Request Body:**
```json
{
    "product": 1,
    "quantity": 2
}
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

### 44. Update Cart Item
**PUT** `/cart/{item_id}/`

**Description:**### 44. Update Cart Item quantity

**Request Body:**
```json
{
    "quantity": 3
}
```

---

### 45. Remove Cart Item
**DELETE** `/cart/{item_id}/`

**Description:** Remove item from cart

**Response (204 No Content):**
```
No content
```

---

## Wishlist APIs

### 46. Get Wishlist
**GET** `/wishlist/`

**Description:** Get user's wishlist

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

### 47. Add to Wishlist
**POST** `/wishlist/`

**Description:** Add product to wishlist

**Request Body:**
```json
{
    "product": 3
}
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

### 48. Remove from Wishlist
**DELETE** `/wishlist/{item_id}/`

**Description:** Remove item from wishlist

**Response (204 No Content):**
```
No content
```

---

## Search APIs

### 49. Product Search
**GET** `/search/`

**Description:** Search products

**Query Parameters:**
- `q`: Search query
- `category`: Filter by category
- `material`: Filter by material
- `gemstone`: Filter by gemstone
- `min_price`: Minimum price
- `max_price`: Maximum price
- `jewelry_type`: Filter by jewelry type
- `ordering`: Sort order

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

## Order APIs

### 50. Get Orders
**GET** `/orders/`

**Description:** Get user's orders

**Query Parameters:**
- `status`: Filter by order status
- `payment_status`: Filter by payment status
- `date_from`: Filter orders from date
- `date_to`: Filter orders to date
- `page`: Page number
- `page_size`: Items per page

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

### 51. Create Order
**POST** `/orders/create/`

**Description:** Create new order from cart

**Request Body:**
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

### 52. Get Order Detail
**GET** `/orders/{id}/`

**Description:** Get specific order details

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

## Payment APIs

### 53. Get Payments
**GET** `/payments/`

**Description:** Get user's payments

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
        "transaction_id": "TXN12345678",
        "created_at": "2024-01-01T10:00:00Z",
        "completed_at": "2024-01-01T10:05:00Z"
    }
]
```

---

### 54. Get Payment Detail
**GET** `/payments/{id}/`

**Description:** Get specific payment details

**Response (200 OK):**
```json
{
    "id": 1,
    "order": {
        "id": 1,
        "order_number": "ORD-20240101-001",
        "status": "delivered",
        "total_amount": "324.99"
    },
    "payment_method": "credit_card",
    "amount": "324.99",
    "status": "completed",
    "transaction_id": "TXN12345678",
    "created_at": "2024-01-01T10:00:00Z",
    "completed_at": "2024-01-01T10:05:00Z"
}
```

---

## Coupon APIs

### 55. Get Coupons
**GET** `/coupons/`

**Description:** Get available coupons

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

### 56. Validate Coupon
**POST** `/coupons/validate/`

**Description:**### 56. Validate Coupon code

**Request Body:**
```json
{
    "code": "SAVE10",
    "order_amount": "100.00"
}
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

### 57. Get Coupon Usage
**GET** `/coupons/usage/`

**Description:** Get user's coupon usage history

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

## Error Responses

### Common Error Codes

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

## Authentication Flow

1. **Register**: POST `/auth/register/`
2. **Verify Email**: GET `/auth/verify-email/?uid={uid}&token={token}`
3. **Login**: POST `/auth/login/`
4. **Use Access Token**: Include `Authorization: Bearer <access_token>` in headers
5. **Refresh Token**: Use refresh token to get new access token when expired
6. **Logout**: POST `/auth/logout/` with refresh token

---

## Pagination

Most list endpoints support pagination with these query parameters:
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)

**Paginated Response Format:**
```json
{
    "count": 100,
    "next": "http://localhost:8000/api/endpoint/?page=3",
    "previous": "http://localhost:8000/api/endpoint/?page=1",
    "results": [...]
}
```

---

## Filtering and Searching

Many endpoints support filtering and searching:

**Common Query Parameters:**
- `search`: Text search across relevant fields
- `ordering`: Sort by field (prefix with `-` for descending)
- `page`: Page number for pagination
- `page_size`: Items per page

**Example:**
```
GET /products/?search=gold&category=rings&min_price=100&max_price=500&ordering=-price&page=1&page_size=10
```

---

## Rate Limiting

API requests are rate-limited to prevent abuse. If you exceed the limit, you'll receive a 429 status code.

---

## Versioning

Current API version: v1
Base URL includes version: `http://localhost:8000/`

---

## Support

For API support and questions, please contact the development team.
