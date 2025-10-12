"""Pydantic schemas for request and response validation."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr


# User Schemas
class UserBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class User(UserBase):
    user_id: int
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


# Category Schemas
class CategoryBase(BaseModel):
    category_name: str
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    category_name: Optional[str] = None
    description: Optional[str] = None


class Category(CategoryBase):
    category_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Product Schemas
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock_qty: int
    category_id: int
    brand: Optional[str] = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock_qty: Optional[int] = None
    category_id: Optional[int] = None
    brand: Optional[str] = None


class Product(ProductBase):
    product_id: int
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


# Order Schemas
class OrderBase(BaseModel):
    user_id: int
    total_amount: float
    shipping_address: str


class OrderCreate(OrderBase):
    pass


class OrderUpdate(BaseModel):
    status: Optional[str] = None
    total_amount: Optional[float] = None
    shipping_address: Optional[str] = None


class Order(OrderBase):
    order_id: int
    order_date: datetime
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# OrderItem Schemas
class OrderItemBase(BaseModel):
    order_id: int
    product_id: int
    quantity: int
    unit_price: float
    subtotal: float


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemUpdate(BaseModel):
    quantity: Optional[int] = None
    unit_price: Optional[float] = None
    subtotal: Optional[float] = None


class OrderItem(OrderItemBase):
    order_item_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Cart Schemas
class CartBase(BaseModel):
    user_id: int


class CartCreate(CartBase):
    pass


class Cart(CartBase):
    cart_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# CartItem Schemas
class CartItemBase(BaseModel):
    cart_id: int
    product_id: int
    quantity: int


class CartItemCreate(CartItemBase):
    pass


class CartItemUpdate(BaseModel):
    quantity: Optional[int] = None


class CartItem(CartItemBase):
    cart_item_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Payment Schemas
class PaymentBase(BaseModel):
    order_id: int
    payment_method: str
    amount: float
    transaction_id: Optional[str] = None


class PaymentCreate(PaymentBase):
    pass


class PaymentUpdate(BaseModel):
    payment_method: Optional[str] = None
    amount: Optional[float] = None
    status: Optional[str] = None
    transaction_id: Optional[str] = None


class Payment(PaymentBase):
    payment_id: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# Review Schemas
class ReviewBase(BaseModel):
    user_id: int
    product_id: int
    rating: int
    comment: Optional[str] = None


class ReviewCreate(ReviewBase):
    pass


class ReviewUpdate(BaseModel):
    rating: Optional[int] = None
    comment: Optional[str] = None


class Review(ReviewBase):
    review_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Shipping Schemas
class ShippingBase(BaseModel):
    order_id: int
    courier_name: str
    tracking_number: Optional[str] = None
    estimated_delivery: Optional[datetime] = None


class ShippingCreate(ShippingBase):
    pass


class ShippingUpdate(BaseModel):
    courier_name: Optional[str] = None
    tracking_number: Optional[str] = None
    status: Optional[str] = None
    estimated_delivery: Optional[datetime] = None
    delivered_at: Optional[datetime] = None


class Shipping(ShippingBase):
    shipment_id: int
    status: str
    delivered_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True