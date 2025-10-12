"""Cart-related functionality for the e-commerce platform."""

from sqlalchemy.orm import Session
from typing import List, Optional
from . import models, schemas

def get_cart_by_user_id(db: Session, user_id: int) -> Optional[models.Cart]:
    """Get cart for a specific user."""
    return db.query(models.Cart).filter(models.Cart.user_id == user_id).first()

def create_cart(db: Session, user_id: int) -> models.Cart:
    """Create a new cart for a user."""
    db_cart = models.Cart(user_id=user_id)
    db.add(db_cart)
    db.commit()
    db.refresh(db_cart)
    return db_cart

def get_or_create_cart(db: Session, user_id: int) -> models.Cart:
    """Get existing cart or create new one for user."""
    cart = get_cart_by_user_id(db, user_id)
    if not cart:
        cart = create_cart(db, user_id)
    return cart

def add_item_to_cart(db: Session, cart_item: schemas.CartItemCreate) -> models.CartItem:
    """Add an item to the cart."""
    # Get or create cart
    cart = get_or_create_cart(db, cart_item.cart_id)
    
    # Check if item already exists in cart
    existing_item = db.query(models.CartItem).filter(
        models.CartItem.cart_id == cart.id,
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
        db_cart_item = models.CartItem(
            cart_id=cart.id,
            product_id=cart_item.product_id,
            quantity=cart_item.quantity
        )
        db.add(db_cart_item)
        db.commit()
        db.refresh(db_cart_item)
        return db_cart_item

def remove_item_from_cart(db: Session, cart_id: int, product_id: int) -> bool:
    """Remove an item from the cart."""
    cart_item = db.query(models.CartItem).filter(
        models.CartItem.cart_id == cart_id,
        models.CartItem.product_id == product_id
    ).first()
    
    if cart_item:
        db.delete(cart_item)
        db.commit()
        return True
    return False

def update_cart_item_quantity(db: Session, cart_id: int, product_id: int, quantity: int) -> Optional[models.CartItem]:
    """Update the quantity of an item in the cart."""
    cart_item = db.query(models.CartItem).filter(
        models.CartItem.cart_id == cart_id,
        models.CartItem.product_id == product_id
    ).first()
    
    if cart_item:
        cart_item.quantity = quantity
        db.commit()
        db.refresh(cart_item)
        return cart_item
    return None

def get_cart_items(db: Session, cart_id: int) -> List[models.CartItem]:
    """Get all items in a cart."""
    return db.query(models.CartItem).filter(models.CartItem.cart_id == cart_id).all()

def clear_cart(db: Session, cart_id: int) -> bool:
    """Clear all items from a cart."""
    cart_items = db.query(models.CartItem).filter(models.CartItem.cart_id == cart_id).all()
    for item in cart_items:
        db.delete(item)
    db.commit()
    return True

def get_cart_total(db: Session, cart_id: int) -> float:
    """Calculate the total value of items in the cart."""
    cart_items = get_cart_items(db, cart_id)
    total = 0.0
    for item in cart_items:
        if item.product:
            total += item.product.price * item.quantity
    return total
