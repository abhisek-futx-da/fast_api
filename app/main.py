"""FastAPI E-Commerce Platform Application."""

from fastapi import FastAPI, Depends, HTTPException, status, Header, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
import jwt
from datetime import datetime, timedelta
from pydantic import BaseModel


from . import crud, models, schemas
from .database import get_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple auth configuration (temporary for testing)
SECRET_KEY = "your-secret-key-change-in-production"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Simple token storage (in production, use Redis or database)
active_tokens = {}

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create simple access token."""
    user_id = data.get("sub")
    token = f"token_{user_id}_{datetime.utcnow().timestamp()}"
    active_tokens[token] = {"user_id": int(user_id), "expires": datetime.utcnow() + timedelta(minutes=30)}
    return token

def verify_token(token: str) -> Optional[dict]:
    """Verify token and return token data."""
    if token in active_tokens:
        token_data = active_tokens[token]
        if datetime.utcnow() < token_data["expires"]:
            return token_data
        else:
            # Token expired, remove it
            del active_tokens[token]
    return None

def get_current_user_id(token: str = Header(None)) -> int:
    """Get current user ID from token in Authorization header."""
    if not token or not token.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    token = token.split(" ")[1]
    token_data = verify_token(token)
    if token_data is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return token_data["user_id"]

def get_current_admin(token: str = Header(
        ...,  # required
        description="Authorization header. Example: Bearer <token>"
    ), db: Session = Depends(get_db)) -> models.Admin:
    """Get current admin from token in Authorization header."""
    print(token)
    if not token or not token.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    token = token.split(" ")[1]
    token_data = verify_token(token)
    if token_data is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    # Get admin by admin_id from token
    admin_id = token_data["user_id"]  # In our case, user_id in token is actually admin_id for admin tokens
    admin = crud.get_admin(db, admin_id)
    if not admin or not admin.is_active:
        raise HTTPException(status_code=403, detail="Admin access required")
    return admin

app = FastAPI(
    title="E-Commerce Platform API",
    description="A comprehensive e-commerce platform built with FastAPI, SQLAlchemy, and PostgreSQL",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    
)

# Root endpoint
@app.get("/", response_model=dict)
def read_root():
    """Welcome message."""
    return {
        "message": "Welcome to E-Commerce Platform API",
        "description": "A comprehensive e-commerce platform built with FastAPI, SQLAlchemy, and PostgreSQL",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

# Health check endpoint
@app.get("/health", response_model=dict)
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "E-Commerce API is running"}

@app.get("/test-auth")
def test_auth_endpoint():
    """Test authentication endpoint."""
    try:
        # Test JWT creation
        test_token = create_access_token(data={"sub": "1"})
        return {"message": "Auth system working", "test_token": test_token}
    except Exception as e:
        return {"error": str(e)}

# ==================== ADMIN ENDPOINTS ====================

@app.post("/admins/", response_model=schemas.Admin, status_code=status.HTTP_201_CREATED)
def create_admin(admin: schemas.AdminCreate, db: Session = Depends(get_db)):
    try:
        # Check for existing username
        existing_username = crud.get_admin_by_username(db, admin.username)
        if existing_username:
            raise HTTPException(status_code=400, detail="Username already exists")
        
        # Check for existing email
        existing_email = db.query(models.Admin).filter(models.Admin.email == admin.email).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already exists")
        
        return crud.create_admin(db=db, admin=admin)
    except HTTPException:
        # Re-raise HTTP exceptions (like duplicate username/email)
        raise
    except Exception as e:
        # Handle any other database errors
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create admin: {str(e)}")


@app.get("/admins/", response_model=List[schemas.Admin])
def list_admins(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_admins(db, skip=skip, limit=limit)


@app.get("/admins/{admin_id}", response_model=schemas.Admin)
def get_admin(admin_id: int, db: Session = Depends(get_db)):
    admin = crud.get_admin(db, admin_id)
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    return admin


@app.put("/admins/{admin_id}", response_model=schemas.Admin)
def update_admin(admin_id: int, payload: schemas.AdminUpdate, db: Session = Depends(get_db)):
    admin = crud.update_admin(db, admin_id, payload)
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    return admin


@app.delete("/admins/{admin_id}", response_model=schemas.Admin)
def delete_admin(admin_id: int, db: Session = Depends(get_db)):
    admin = crud.delete_admin(db, admin_id)
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    return admin

# ==================== USER ENDPOINTS ====================

@app.post("/users/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Create a new user with proper password hashing."""
    try:
        db_user = crud.get_user_by_email(db, email=user.email)
        if db_user:
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )
        return crud.create_user(db=db, user=user)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create user: {str(e)}"
        )

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/auth/login")
def login_user(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Login user and return JWT token."""
    user = crud.get_user_by_email(db, email=login_data.email)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )
    
    # Verify password with proper hashing
    if not crud.verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Invalid password"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.user_id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "user_id": user.user_id}

@app.post("/auth/admin-login")
def login_admin(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Login admin and return JWT token."""
    admin = crud.get_admin_by_username(db, username=login_data.username)  # Using email field as username for login
    if not admin:
        raise HTTPException(
            status_code=401,
            detail="Admin not found"
        )
    
    # Verify password with proper hashing
    if not crud.verify_password(login_data.password, admin.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Invalid password"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(admin.admin_id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "admin_id": admin.admin_id, "role": admin.role}

@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all users with pagination."""
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """Get a specific user by ID."""
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.put("/users/{user_id}", response_model=schemas.User)
def update_user(user_id: int, user: schemas.UserUpdate, db: Session = Depends(get_db)):
    """Update user details."""
    db_user = crud.update_user(db, user_id=user_id, user_update=user)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.delete("/users/{user_id}", response_model=schemas.User)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Delete a user (soft delete)."""
    db_user = crud.delete_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# ==================== CATEGORY ENDPOINTS ====================

@app.post("/categories/", response_model=schemas.Category, status_code=status.HTTP_201_CREATED)
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    """Create a new category."""
    return crud.create_category(db=db, category=category)

@app.get("/categories/", response_model=List[schemas.Category])
def read_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all categories."""
    return crud.get_categories(db, skip=skip, limit=limit)

@app.get("/categories/{category_id}", response_model=schemas.Category)
def read_category(category_id: int, db: Session = Depends(get_db)):
    """Get a specific category by ID."""
    db_category = crud.get_category(db, category_id=category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return db_category

# ==================== PRODUCT ENDPOINTS ====================

@app.post("/products/", response_model=schemas.Product, status_code=status.HTTP_201_CREATED)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    """Create a new product."""
    return crud.create_product(db=db, product=product)

@app.get("/products/", response_model=List[schemas.Product])
def read_products(
    skip: int = 0, 
    limit: int = 100, 
    category_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get all products with optional category filter."""
    return crud.get_products(db, skip=skip, limit=limit, category_id=category_id)

@app.get("/products/search/", response_model=List[schemas.Product])
def search_products(
    q: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Search products by name or description."""
    return crud.search_products(db, search_term=q, skip=skip, limit=limit)

@app.get("/products/{product_id}", response_model=schemas.Product)
def read_product(product_id: int, db: Session = Depends(get_db)):
    """Get a specific product by ID."""
    db_product = crud.get_product(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

# ==================== INVENTORY ENDPOINTS ====================

@app.post("/inventory/{product_id}/set", response_model=schemas.Product)
def set_inventory(product_id: int, new_stock: int = 0, db: Session = Depends(get_db)):
    product = crud.set_product_stock(db, product_id, new_stock)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.post("/inventory/{product_id}/increment", response_model=schemas.Product)
def increment_inventory(product_id: int, delta: int = 0, db: Session = Depends(get_db)):
    product = crud.increment_product_stock(db, product_id, delta)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

# ==================== ADMIN ENDPOINTS ====================

# Admin Product Management
@app.get("/admin/products/", response_model=List[schemas.Product])
def admin_get_products(skip: int = 0, limit: int = 100, admin: models.Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    """Get all products. Admin only."""
    return crud.get_products(db, skip=skip, limit=limit)

@app.post("/admin/products/", response_model=schemas.Product, status_code=status.HTTP_201_CREATED)
def admin_create_product(product: schemas.ProductCreate, admin: models.Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    """Create a new product. Admin only."""
    return crud.create_product(db=db, product=product)

@app.get("/admin/products/{product_id}", response_model=schemas.Product)
def admin_get_product(product_id: int, admin: models.Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    """Get a specific product by ID. Admin only."""
    db_product = crud.get_product(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

@app.put("/admin/products/{product_id}", response_model=schemas.Product)
def admin_update_product(product_id: int, product_update: schemas.ProductUpdate, admin: models.Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    """Update a product. Admin only."""
    db_product = crud.update_product(db, product_id, product_update)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

@app.delete("/admin/products/{product_id}")
def admin_delete_product(product_id: int, admin: models.Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    """Delete a product. Admin only."""
    success = crud.delete_product(db, product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}

# Admin Inventory Management
@app.post("/admin/inventory/{product_id}/set", response_model=schemas.Product)
def admin_set_inventory(product_id: int, new_stock: int = 0, admin: models.Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    """Set product stock. Admin only."""
    product = crud.set_product_stock(db, product_id, new_stock)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.post("/admin/inventory/{product_id}/increment", response_model=schemas.Product)
def admin_increment_inventory(product_id: int, delta: int = 0, admin: models.Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    """Increment product stock. Admin only."""
    product = crud.increment_product_stock(db, product_id, delta)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

# Admin User Management
@app.get("/admin/users/", response_model=List[schemas.User])
def admin_get_users(skip: int = 0, limit: int = 100, admin: models.Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    """Get all users. Admin only."""
    return crud.get_users(db, skip=skip, limit=limit)

@app.delete("/admin/users/{user_id}")
def admin_delete_user(user_id: int, admin: models.Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    """Delete a user. Admin only."""
    success = crud.delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}

@app.put("/admin/users/{user_id}/status")
def admin_update_user_status(user_id: int, is_active: bool, admin: models.Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    """Update user active status. Admin only."""
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = is_active
    db.commit()
    db.refresh(user)
    return {"message": f"User {'activated' if is_active else 'deactivated'} successfully"}

# Admin Review Management
@app.get("/admin/reviews/", response_model=List[schemas.Review])
def admin_get_reviews(skip: int = 0, limit: int = 100, admin: models.Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    """Get all reviews. Admin only."""
    return crud.get_reviews(db, skip=skip, limit=limit)

@app.delete("/admin/reviews/{review_id}")
def admin_delete_review(review_id: int, admin: models.Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    """Delete a review. Admin only."""
    success = crud.delete_review(db, review_id)
    if not success:
        raise HTTPException(status_code=404, detail="Review not found")
    return {"message": "Review deleted successfully"}

# Admin Pricing Management
@app.put("/admin/pricing/{product_id}")
def admin_update_product_price(product_id: int, new_price: float, admin: models.Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    """Update product price. Admin only."""
    product = crud.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product.price = new_price
    db.commit()
    db.refresh(product)
    return {"message": f"Product price updated to ${new_price}", "product": product}

# ==================== CART ENDPOINTS ====================

@app.get("/users/{user_id}/cart", response_model=schemas.Cart)
def get_user_cart(user_id: int, current_user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """Get user's cart. Requires authentication."""
    if current_user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this cart")
    cart = crud.get_or_create_cart(db, user_id=user_id)
    return cart

@app.post("/cart/items/", response_model=schemas.CartItem, status_code=status.HTTP_201_CREATED)
def add_to_cart(cart_item: schemas.CartItemCreate, current_user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """Add a product to cart. Requires authentication."""
    # Verify the cart belongs to the authenticated user
    cart = crud.get_cart(db, cart_item.cart_id)
    if not cart or cart.user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Not authorized to add items to this cart")
    return crud.add_to_cart(db=db, cart_item=cart_item)

@app.get("/cart/{cart_id}/items/", response_model=List[schemas.CartItem])
def get_cart_items(cart_id: int, current_user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """Get all items in a cart. Requires authentication."""
    # Verify the cart belongs to the authenticated user
    cart = crud.get_cart(db, cart_id)
    if not cart or cart.user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this cart")
    return crud.get_cart_items(db, cart_id=cart_id)

# ==================== ORDER ENDPOINTS ====================

@app.post("/orders/", response_model=schemas.Order, status_code=status.HTTP_201_CREATED)
def create_order(order: schemas.OrderCreate, current_user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """Create a new order. Requires authentication."""
    if order.user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Not authorized to create order for this user")
    return crud.create_order(db=db, order=order)

@app.get("/orders/", response_model=List[schemas.Order])
def read_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all orders. (Admin only - no auth for now)"""
    return crud.get_orders(db, skip=skip, limit=limit)

@app.get("/orders/{order_id}", response_model=schemas.Order)
def read_order(order_id: int, current_user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """Get a specific order by ID. Requires authentication."""
    db_order = crud.get_order(db, order_id=order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    if db_order.user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this order")
    return db_order

@app.get("/users/{user_id}/orders/", response_model=List[schemas.Order])
def read_user_orders(user_id: int, current_user_id: int = Depends(get_current_user_id), skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get orders by user ID. Requires authentication."""
    if user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this user's orders")
    return crud.get_orders_by_user(db, user_id=user_id, skip=skip, limit=limit)

# ==================== ORDER ITEM ENDPOINTS ====================

@app.post("/order-items/", response_model=schemas.OrderItem, status_code=status.HTTP_201_CREATED)
def create_order_item(order_item: schemas.OrderItemCreate, current_user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """Create a new order item. Requires authentication."""
    # Verify the order belongs to the authenticated user
    order = crud.get_order(db, order_item.order_id)
    if not order or order.user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Not authorized to add items to this order")
    return crud.create_order_item(db=db, order_item=order_item)

@app.get("/orders/{order_id}/items/", response_model=List[schemas.OrderItem])
def get_order_items(order_id: int, current_user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """Get all items in an order. Requires authentication."""
    # Verify the order belongs to the authenticated user
    order = crud.get_order(db, order_id)
    if not order or order.user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this order's items")
    return crud.get_order_items(db, order_id=order_id)

# ==================== PAYMENT ENDPOINTS ====================

@app.post("/payments/", response_model=schemas.Payment, status_code=status.HTTP_201_CREATED)
def create_payment(payment: schemas.PaymentCreate, db: Session = Depends(get_db)):
    """Create a new payment."""
    return crud.create_payment(db=db, payment=payment)

@app.get("/payments/{payment_id}", response_model=schemas.Payment)
def read_payment(payment_id: int, db: Session = Depends(get_db)):
    """Get a specific payment by ID."""
    db_payment = crud.get_payment(db, payment_id=payment_id)
    if db_payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    return db_payment

# ==================== REVIEW ENDPOINTS ====================

@app.post("/reviews/", response_model=schemas.Review, status_code=status.HTTP_201_CREATED)
def create_review(review: schemas.ReviewCreate, db: Session = Depends(get_db)):
    """Create a new review."""
    return crud.create_review(db=db, review=review)

@app.get("/reviews/{review_id}", response_model=schemas.Review)
def read_review(review_id: int, db: Session = Depends(get_db)):
    """Get a specific review by ID."""
    db_review = crud.get_review(db, review_id=review_id)
    if db_review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    return db_review

@app.get("/products/{product_id}/reviews/", response_model=List[schemas.Review])
def read_product_reviews(product_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get reviews for a specific product."""
    return crud.get_reviews_by_product(db, product_id=product_id, skip=skip, limit=limit)

# ==================== SHIPPING ENDPOINTS ====================

@app.post("/shipping/", response_model=schemas.Shipping, status_code=status.HTTP_201_CREATED)
def create_shipping(shipping: schemas.ShippingCreate, db: Session = Depends(get_db)):
    """Create a new shipping record."""
    return crud.create_shipping(db=db, shipping=shipping)

@app.get("/shipping/{shipment_id}", response_model=schemas.Shipping)
def read_shipping(shipment_id: int, db: Session = Depends(get_db)):
    """Get a specific shipping record by ID."""
    db_shipping = crud.get_shipping(db, shipment_id=shipment_id)
    if db_shipping is None:
        raise HTTPException(status_code=404, detail="Shipping record not found")
    return db_shipping

# ==================== STATISTICS ENDPOINTS ====================

@app.get("/stats/products")
def get_product_stats(db: Session = Depends(get_db)):
    """Get product statistics."""
    total_products = db.query(models.Product).count()
    active_products = db.query(models.Product).filter(models.Product.is_active == True).count()
    low_stock_products = db.query(models.Product).filter(models.Product.stock_qty < 10).count()
    
    return {
        "total_products": total_products,
        "active_products": active_products,
        "low_stock_products": low_stock_products
    }

@app.get("/stats/users")
def get_user_stats(db: Session = Depends(get_db)):
    """Get user statistics."""
    total_users = db.query(models.User).count()
    active_users = db.query(models.User).filter(models.User.is_active == True).count()
    
    return {
        "total_users": total_users,
        "active_users": active_users
    }

@app.get("/stats/orders")
def get_order_stats(db: Session = Depends(get_db)):
    """Get order statistics."""
    total_orders = db.query(models.Order).count()
    pending_orders = db.query(models.Order).filter(models.Order.status == "pending").count()
    completed_orders = db.query(models.Order).filter(models.Order.status == "completed").count()
    
    return {
        "total_orders": total_orders,
        "pending_orders": pending_orders,
        "completed_orders": completed_orders
    }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(status_code=404, content={"detail": "Resource not found"})

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})