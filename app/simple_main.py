"""Simplified FastAPI E-Commerce Platform Application."""

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from . import crud, models, schemas
from .database import get_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="E-Commerce Platform API",
    description="A comprehensive e-commerce platform built with FastAPI, SQLAlchemy, and PostgreSQL",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
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

# ==================== USER ENDPOINTS ====================

@app.post("/users/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Create a new user."""
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    return crud.create_user(db=db, user=user)


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

# ==================== PRODUCT ENDPOINTS ====================

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

# ==================== CART ENDPOINTS ====================

@app.get("/users/{user_id}/cart", response_model=schemas.Cart)
def get_user_cart(user_id: int, db: Session = Depends(get_db)):
    """Get user's cart."""
    cart = crud.get_or_create_cart(db, user_id=user_id)
    return cart


@app.post("/cart/items/", response_model=schemas.CartItem, status_code=status.HTTP_201_CREATED)
def add_to_cart(cart_item: schemas.CartItemCreate, db: Session = Depends(get_db)):
    """Add a product to cart."""
    return crud.add_to_cart(db=db, cart_item=cart_item)


@app.get("/cart/{cart_id}/items/", response_model=List[schemas.CartItem])
def get_cart_items(cart_id: int, db: Session = Depends(get_db)):
    """Get all items in a cart."""
    return crud.get_cart_items(db, cart_id=cart_id)

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

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {"detail": "Resource not found"}


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {exc}")
    return {"detail": "Internal server error"}
