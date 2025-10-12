# E-Commerce Platform ER Diagram (Mermaid)

```mermaid
erDiagram
    USERS {
        int id PK
        string name
        string email UK
        string password_hash
        string phone_number
        string address
        datetime created_at
        boolean is_active
    }
    
    CATEGORIES {
        int id PK
        string category_name UK
        text description
        datetime created_at
    }
    
    PRODUCTS {
        int id PK
        string name
        text description
        float price
        int stock_qty
        string brand
        int category_id FK
        datetime created_at
        boolean is_active
    }
    
    CARTS {
        int id PK
        int user_id FK
        datetime created_at
        datetime updated_at
    }
    
    CART_ITEMS {
        int id PK
        int cart_id FK
        int product_id FK
        int quantity
        datetime created_at
    }
    
    ORDERS {
        int id PK
        int user_id FK
        datetime order_date
        float total_amount
        string status
        string shipping_address
        datetime created_at
    }
    
    ORDER_ITEMS {
        int id PK
        int order_id FK
        int product_id FK
        int quantity
        float price_at_time
        datetime created_at
    }
    
    PAYMENTS {
        int id PK
        int order_id FK
        string payment_method
        float amount
        string payment_status
        string transaction_id
        datetime payment_date
    }
    
    REVIEWS {
        int id PK
        int user_id FK
        int product_id FK
        int rating
        text comment
        datetime created_at
    }
    
    SHIPPING {
        int id PK
        int order_id FK
        string shipping_address
        string tracking_number
        string shipping_status
        datetime estimated_delivery
        datetime actual_delivery
    }
    
    ADMINS {
        int id PK
        string username UK
        string email UK
        string password_hash
        string role
        boolean is_active
        datetime created_at
    }
    
    COUPONS {
        int id PK
        string code UK
        string discount_type
        float discount_value
        float min_order_amount
        float max_discount
        int usage_limit
        int used_count
        datetime valid_from
        datetime valid_until
        boolean is_active
    }
    
    WISHLIST {
        int id PK
        int user_id FK
        int product_id FK
        datetime created_at
    }
    
    AUDIT_LOGS {
        int id PK
        int admin_id FK
        string action
        string table_name
        int record_id
        json old_values
        json new_values
        datetime timestamp
    }

    %% Relationships
    USERS ||--o{ CARTS : "has"
    USERS ||--o{ ORDERS : "places"
    USERS ||--o{ REVIEWS : "writes"
    USERS ||--o{ WISHLIST : "maintains"
    
    CATEGORIES ||--o{ PRODUCTS : "contains"
    
    PRODUCTS ||--o{ CART_ITEMS : "added_to"
    PRODUCTS ||--o{ ORDER_ITEMS : "ordered_in"
    PRODUCTS ||--o{ REVIEWS : "reviewed_in"
    PRODUCTS ||--o{ WISHLIST : "wished_for"
    
    CARTS ||--o{ CART_ITEMS : "contains"
    
    ORDERS ||--o{ ORDER_ITEMS : "contains"
    ORDERS ||--|| PAYMENTS : "paid_by"
    ORDERS ||--|| SHIPPING : "shipped_via"
    ORDERS }o--|| COUPONS : "uses"
    
    ADMINS ||--o{ AUDIT_LOGS : "performs"
```

## Entity Descriptions

### Core Business Entities

**USERS**: Customer accounts with authentication and profile information
- Unique email constraint for login
- Soft delete capability with is_active flag
- Tracks creation timestamp

**CATEGORIES**: Product classification system
- Hierarchical organization of products
- Unique category names to prevent duplicates

**PRODUCTS**: Catalog items available for purchase
- Links to categories for organization
- Stock quantity tracking for inventory management
- Price and brand information
- Soft delete with is_active flag

### Shopping Cart System

**CARTS**: User shopping baskets
- One cart per user (1:1 relationship)
- Tracks creation and last update timestamps

**CART_ITEMS**: Individual items in shopping carts
- Links products to carts with quantities
- Allows multiple quantities of same product

### Order Management

**ORDERS**: Customer purchase records
- Links to user who placed the order
- Tracks total amount and order status
- Includes shipping address for delivery

**ORDER_ITEMS**: Individual products within orders
- Preserves product price at time of purchase
- Tracks quantity ordered

### Payment & Shipping

**PAYMENTS**: Transaction records
- One-to-one with orders
- Tracks payment method and status
- Includes transaction IDs for reconciliation

**SHIPPING**: Delivery information
- One-to-one with orders
- Tracks shipping status and delivery dates
- Includes tracking numbers

### User Experience

**REVIEWS**: Customer feedback on products
- Links users to products with ratings and comments
- Enables product quality tracking

**WISHLIST**: User's saved products
- Many-to-many relationship between users and products
- Allows users to save products for later purchase

### Administrative Features

**ADMINS**: Administrative user accounts
- Separate from customer accounts
- Role-based access control
- Audit trail for administrative actions

**COUPONS**: Discount and promotion system
- Unique coupon codes
- Flexible discount types (percentage or fixed amount)
- Usage limits and validity periods

**AUDIT_LOGS**: Administrative action tracking
- Records all changes made by administrators
- JSON storage for flexible data capture
- Timestamp tracking for compliance

## Key Design Features

1. **Referential Integrity**: All foreign key relationships maintain data consistency
2. **Audit Trail**: Complete tracking of administrative changes
3. **Soft Deletes**: is_active flags preserve data while hiding inactive records
4. **Flexible Pricing**: Order items store price at time of purchase
5. **Scalable Design**: Normalized structure supports growth
6. **User Experience**: Wishlist and review systems enhance customer engagement
