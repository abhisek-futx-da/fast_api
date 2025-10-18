# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Commands

### Development Server
```bash
# Start development server with hot reload
uvicorn app.main:app --reload

# Alternative: Start simple test app
uvicorn test_app:app --reload

# Server runs at http://127.0.0.1:8000
# Interactive API docs at http://127.0.0.1:8000/docs
# Alternative docs at http://127.0.0.1:8000/redoc
```

### Database Operations
```bash
# Apply all pending migrations
alembic upgrade head

# Create new migration from model changes
alembic revision --autogenerate -m "description"

# Rollback last migration
alembic downgrade -1

# Check current migration status
alembic current

# View migration history
alembic history
```

### Environment Setup
```bash
# Activate virtual environment (required before any operations)
source venv/bin/activate  # macOS/Linux
# or
.venv/Scripts/activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Create new virtual environment if needed
python3 -m venv venv
```

### Testing
```bash
# No formal test framework configured
# Manual testing via interactive docs at /docs endpoint
# Test basic functionality with test_app.py
python test_app.py
```

## Architecture Overview

This is a comprehensive FastAPI-based e-commerce platform with a multi-layered architecture:

### Core Application Structure
- **`app/main.py`**: FastAPI application with all REST endpoints, authentication logic, and error handlers
- **`app/models.py`**: SQLAlchemy ORM models defining database schema for e-commerce entities
- **`app/schemas.py`**: Pydantic models for request/response validation and serialization
- **`app/crud.py`**: Database operations layer separating business logic from API endpoints
- **`app/database.py`**: Database configuration, connection management, and session handling

### Database Architecture
The application uses a normalized PostgreSQL schema with 10+ interconnected entities:
- **Core Entities**: Users, Products, Categories, Orders
- **Shopping System**: Cart, CartItem, OrderItem
- **Business Logic**: Payments, Shipping, Reviews
- **Administration**: Admin users with role-based access

Key relationships:
- Users have one-to-many relationships with Cart, Orders, Reviews
- Products belong to Categories and can be in multiple Carts/Orders
- Orders have one-to-one relationships with Payments and Shipping
- Full audit trail through Admin and authentication systems

### Authentication System
- Simple token-based auth with in-memory storage (development only)
- JWT token structure: `token_{user_id}_{timestamp}`
- Protected endpoints use `Authorization: Bearer <token>` headers
- Role separation between regular Users and Admin accounts

### Migration Strategy
Uses Alembic for database versioning with two-stage evolution:
1. Initial table creation with core columns
2. Schema evolution by adding fields to existing tables
3. Automatic migration generation via `--autogenerate`

## Development Patterns

### Error Handling
- Consistent HTTPException usage with appropriate status codes
- Centralized error handlers for 404 and 500 responses
- Database integrity validation in CRUD operations

### CRUD Operations
- Separation of concerns: endpoints call CRUD functions, never direct database access
- Soft delete pattern using `is_active` flags
- Password hashing with bcrypt (72-byte limit enforced)
- Pagination support with `skip` and `limit` parameters

### API Design
- RESTful endpoint structure with proper HTTP verbs
- Resource-based URLs: `/users/{user_id}`, `/products/{product_id}`
- Protected endpoints require user authentication and ownership verification
- Statistics endpoints for reporting: `/stats/users`, `/stats/products`, `/stats/orders`

### Database Connection
- Connection string format: `postgresql://user:password@host/database`
- Must update both `app/database.py` and `alembic.ini` when changing database
- Session management via dependency injection with `get_db()`

## Key Implementation Details

### Authentication Flow
1. User login via `/auth/login` returns access token
2. Protected endpoints extract token from Authorization header
3. Token verification checks expiration and maps to user_id
4. Resource access requires ownership verification (user can only access their own data)

### Database Migrations
- Migration files in `alembic/versions/` contain both upgrade and downgrade functions
- Environment configuration in `alembic/env.py` links to SQLAlchemy models
- Database URL must be URL-encoded (especially passwords with special characters)

### Inventory Management
- Stock quantity tracking with automatic minimum enforcement (>= 0)
- Dedicated endpoints for setting and incrementing stock levels
- Integration with order processing for stock deduction

### E-commerce Workflow
1. User browses products (public endpoints)
2. User adds items to cart (requires authentication)
3. User creates order from cart items
4. Payment processing creates payment record
5. Order fulfillment creates shipping record
6. Users can leave reviews after purchase

## Common Issues & Solutions

### Alembic Configuration
- Ensure `sqlalchemy.url` in `alembic.ini` matches `DATABASE_URL` in `app/database.py`
- Use double percent signs (%%) to escape % characters in password
- Run `alembic upgrade head` before starting development server

### Password Security
- Passwords are hashed using bcrypt with 72-byte limit
- Never store plain text passwords
- Use `get_password_hash()` and `verify_password()` from CRUD module

### File System Issues
- Verify file saves with `cat filename` or `type filename` in terminal
- Force file saves using "Save As..." if changes don't persist
- Check file permissions if migration files fail to save

## Database Connection Setup

Update these files when changing database connection:
1. `app/database.py`: Update `DATABASE_URL` variable
2. `alembic.ini`: Update `sqlalchemy.url` parameter

Connection string format: `postgresql://username:password@host:port/database_name`