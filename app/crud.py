"""CRUD operations for the e-commerce platform."""

from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from passlib.context import CryptContext
from . import models, schemas

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password."""
    return pwd_context.verify(plain_password, hashed_password)

# User CRUD operations
def get_user(db: Session, user_id: int) -> Optional[models.User]:
    """Get a user by ID."""
    return db.query(models.User).filter(models.User.user_id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """Get a user by email."""
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
    """Get all users with pagination."""
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """Create a new user."""
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        name=user.name,
        email=user.email,
        password_hash=hashed_password,
        phone=user.phone,
        address=user.address
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate) -> Optional[models.User]:
    """Update a user."""
    db_user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if db_user:
        update_data = user_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)
        db.commit()
        db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int) -> Optional[models.User]:
    """Delete a user (soft delete)."""
    db_user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if db_user:
        db_user.is_active = False
        db.commit()
        db.refresh(db_user)
    return db_user

# Category CRUD operations
def get_category(db: Session, category_id: int) -> Optional[models.Category]:
    """Get a category by ID."""
    return db.query(models.Category).filter(models.Category.category_id == category_id).first()

def get_categories(db: Session, skip: int = 0, limit: int = 100) -> List[models.Category]:
    """Get all categories."""
    return db.query(models.Category).offset(skip).limit(limit).all()

def create_category(db: Session, category: schemas.CategoryCreate) -> models.Category:
    """Create a new category."""
    db_category = models.Category(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

# Product CRUD operations
def get_product(db: Session, product_id: int) -> Optional[models.Product]:
    """Get a product by ID."""
    return db.query(models.Product).filter(models.Product.product_id == product_id).first()

def get_products(db: Session, skip: int = 0, limit: int = 100, category_id: Optional[int] = None) -> List[models.Product]:
    """Get all products with optional category filter."""
    query = db.query(models.Product)
    if category_id:
        query = query.filter(models.Product.category_id == category_id)
    return query.offset(skip).limit(limit).all()

def search_products(db: Session, search_term: str, skip: int = 0, limit: int = 100) -> List[models.Product]:
    """Search products by name or description."""
    return db.query(models.Product).filter(
        or_(
            models.Product.name.ilike(f"%{search_term}%"),
            models.Product.description.ilike(f"%{search_term}%")
        )
    ).offset(skip).limit(limit).all()

def create_product(db: Session, product: schemas.ProductCreate) -> models.Product:
    """Create a new product."""
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

# Cart CRUD operations
def get_cart(db: Session, cart_id: int) -> Optional[models.Cart]:
    """Get a cart by ID."""
    return db.query(models.Cart).filter(models.Cart.cart_id == cart_id).first()

def get_cart_by_user(db: Session, user_id: int) -> Optional[models.Cart]:
    """Get a cart by user ID."""
    return db.query(models.Cart).filter(models.Cart.user_id == user_id).first()

def get_or_create_cart(db: Session, user_id: int) -> models.Cart:
    """Get existing cart or create new one for user."""
    cart = get_cart_by_user(db, user_id)
    if not cart:
        cart = models.Cart(user_id=user_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart

def add_to_cart(db: Session, cart_item: schemas.CartItemCreate) -> models.CartItem:
    """Add an item to cart."""
    # Check if item already exists in cart
    existing_item = db.query(models.CartItem).filter(
        models.CartItem.cart_id == cart_item.cart_id,
        models.CartItem.product_id == cart_item.product_id
    ).first()
    
    if existing_item:
        # Update quantity
        existing_item.quantity += cart_item.quantity
        db.commit()
        db.refresh(existing_item)
        return existing_item
    else:
        # Create new cart item
        db_cart_item = models.CartItem(**cart_item.dict())
        db.add(db_cart_item)
        db.commit()
        db.refresh(db_cart_item)
        return db_cart_item

def get_cart_items(db: Session, cart_id: int) -> List[models.CartItem]:
    """Get all items in a cart."""
    return db.query(models.CartItem).filter(models.CartItem.cart_id == cart_id).all()

# Order CRUD operations
def get_order(db: Session, order_id: int) -> Optional[models.Order]:
    """Get an order by ID."""
    return db.query(models.Order).filter(models.Order.order_id == order_id).first()

def get_orders(db: Session, skip: int = 0, limit: int = 100) -> List[models.Order]:
    """Get all orders."""
    return db.query(models.Order).offset(skip).limit(limit).all()

def get_orders_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[models.Order]:
    """Get orders by user ID."""
    return db.query(models.Order).filter(models.Order.user_id == user_id).offset(skip).limit(limit).all()

def create_order(db: Session, order: schemas.OrderCreate) -> models.Order:
    """Create a new order."""
    db_order = models.Order(**order.dict())
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

# OrderItem CRUD operations
def create_order_item(db: Session, order_item: schemas.OrderItemCreate) -> models.OrderItem:
    """Create a new order item."""
    db_order_item = models.OrderItem(**order_item.dict())
    db.add(db_order_item)
    db.commit()
    db.refresh(db_order_item)
    return db_order_item

def get_order_items(db: Session, order_id: int) -> List[models.OrderItem]:
    """Get all items in an order."""
    return db.query(models.OrderItem).filter(models.OrderItem.order_id == order_id).all()

# Payment CRUD operations
def get_payment(db: Session, payment_id: int) -> Optional[models.Payment]:
    """Get a payment by ID."""
    return db.query(models.Payment).filter(models.Payment.payment_id == payment_id).first()

def create_payment(db: Session, payment: schemas.PaymentCreate) -> models.Payment:
    """Create a new payment."""
    db_payment = models.Payment(**payment.dict())
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment

# Review CRUD operations
def get_review(db: Session, review_id: int) -> Optional[models.Review]:
    """Get a review by ID."""
    return db.query(models.Review).filter(models.Review.review_id == review_id).first()

def get_reviews_by_product(db: Session, product_id: int, skip: int = 0, limit: int = 100) -> List[models.Review]:
    """Get reviews by product ID."""
    return db.query(models.Review).filter(models.Review.product_id == product_id).offset(skip).limit(limit).all()

def create_review(db: Session, review: schemas.ReviewCreate) -> models.Review:
    """Create a new review."""
    db_review = models.Review(**review.dict())
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review

# Shipping CRUD operations
def get_shipping(db: Session, shipment_id: int) -> Optional[models.Shipping]:
    """Get shipping by ID."""
    return db.query(models.Shipping).filter(models.Shipping.shipment_id == shipment_id).first()

def create_shipping(db: Session, shipping: schemas.ShippingCreate) -> models.Shipping:
    """Create a new shipping record."""
    db_shipping = models.Shipping(**shipping.dict())
    db.add(db_shipping)
    db.commit()
    db.refresh(db_shipping)
    return db_shipping