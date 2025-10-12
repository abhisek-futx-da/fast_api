# E-Commerce Platform ER Diagram Description

## Overview
This document describes the Entity-Relationship (ER) diagram for a comprehensive e-commerce platform built with FastAPI, SQLAlchemy, and PostgreSQL.

## Core Entities

### 1. Users
- **Primary Key**: id (Integer, Auto-increment)
- **Attributes**: name, email (unique), password_hash, phone_number, address, created_at, is_active
- **Relationships**: One-to-Many with Cart, Order, Review, Wishlist

### 2. Categories
- **Primary Key**: id (Integer, Auto-increment)
- **Attributes**: category_name (unique), description, created_at
- **Relationships**: One-to-Many with Products

### 3. Products
- **Primary Key**: id (Integer, Auto-increment)
- **Attributes**: name, description, price, stock_qty, brand, category_id (FK), created_at, is_active
- **Relationships**: Many-to-One with Category, One-to-Many with CartItem, OrderItem, Review, Wishlist

### 4. Cart
- **Primary Key**: id (Integer, Auto-increment)
- **Attributes**: user_id (FK), created_at, updated_at
- **Relationships**: Many-to-One with User, One-to-Many with CartItem

### 5. CartItem
- **Primary Key**: id (Integer, Auto-increment)
- **Attributes**: cart_id (FK), product_id (FK), quantity, created_at
- **Relationships**: Many-to-One with Cart and Product

### 6. Orders
- **Primary Key**: id (Integer, Auto-increment)
- **Attributes**: user_id (FK), order_date, total_amount, status, shipping_address, created_at
- **Relationships**: Many-to-One with User, One-to-Many with OrderItem, One-to-One with Payment, One-to-One with Shipping

### 7. OrderItem
- **Primary Key**: id (Integer, Auto-increment)
- **Attributes**: order_id (FK), product_id (FK), quantity, price_at_time, created_at
- **Relationships**: Many-to-One with Order and Product

### 8. Payments
- **Primary Key**: id (Integer, Auto-increment)
- **Attributes**: order_id (FK), payment_method, amount, payment_status, transaction_id, payment_date
- **Relationships**: One-to-One with Order

### 9. Reviews
- **Primary Key**: id (Integer, Auto-increment)
- **Attributes**: user_id (FK), product_id (FK), rating, comment, created_at
- **Relationships**: Many-to-One with User and Product

### 10. Shipping
- **Primary Key**: id (Integer, Auto-increment)
- **Attributes**: order_id (FK), shipping_address, tracking_number, shipping_status, estimated_delivery, actual_delivery
- **Relationships**: One-to-One with Order

### 11. Admin
- **Primary Key**: id (Integer, Auto-increment)
- **Attributes**: username (unique), email (unique), password_hash, role, is_active, created_at
- **Relationships**: One-to-Many with AuditLog

### 12. Coupons
- **Primary Key**: id (Integer, Auto-increment)
- **Attributes**: code (unique), discount_type, discount_value, min_order_amount, max_discount, usage_limit, used_count, valid_from, valid_until, is_active
- **Relationships**: One-to-Many with Orders

### 13. Wishlist
- **Primary Key**: id (Integer, Auto-increment)
- **Attributes**: user_id (FK), product_id (FK), created_at
- **Relationships**: Many-to-One with User and Product

### 14. AuditLog
- **Primary Key**: id (Integer, Auto-increment)
- **Attributes**: admin_id (FK), action, table_name, record_id, old_values, new_values, timestamp
- **Relationships**: Many-to-One with Admin

## Key Relationships

### One-to-Many Relationships:
- User → Cart, Order, Review, Wishlist
- Category → Product
- Cart → CartItem
- Order → OrderItem
- Product → CartItem, OrderItem, Review, Wishlist
- Admin → AuditLog
- Coupon → Order

### One-to-One Relationships:
- Order ↔ Payment
- Order ↔ Shipping

### Many-to-Many Relationships:
- User ↔ Product (through Wishlist)
- User ↔ Product (through CartItem)
- User ↔ Product (through OrderItem)

## Database Design Principles

1. **Normalization**: Tables are normalized to 3NF to reduce redundancy
2. **Referential Integrity**: Foreign key constraints ensure data consistency
3. **Indexing**: Strategic indexes on frequently queried columns
4. **Audit Trail**: AuditLog table tracks all administrative changes
5. **Soft Deletes**: is_active flags for soft deletion of records
6. **Timestamps**: created_at and updated_at for tracking record lifecycle

## Scalability Considerations

1. **Partitioning**: Large tables can be partitioned by date or user_id
2. **Caching**: Frequently accessed data can be cached
3. **Read Replicas**: Database read replicas for improved performance
4. **Connection Pooling**: Efficient database connection management
