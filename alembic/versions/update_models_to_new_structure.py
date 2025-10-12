"""Update models to new structure

Revision ID: update_models_001
Revises: ecommerce_001
Create Date: 2025-01-12 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'update_models_001'
down_revision = 'ecommerce_001'
branch_labels = None
depends_on = None


def upgrade():
    # Rename existing tables and columns to match new structure
    
    # Rename users table columns
    op.alter_column('users', 'id', new_column_name='user_id')
    op.alter_column('users', 'phone_number', new_column_name='phone')
    
    # Rename categories table columns
    op.alter_column('categories', 'id', new_column_name='category_id')
    
    # Rename products table columns
    op.alter_column('products', 'id', new_column_name='product_id')
    
    # Rename carts table columns
    op.alter_column('carts', 'id', new_column_name='cart_id')
    
    # Create new tables that don't exist yet
    op.create_table('orders',
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('order_date', sa.DateTime(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('total_amount', sa.Float(), nullable=False),
        sa.Column('shipping_address', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('order_id')
    )
    op.create_index(op.f('ix_orders_order_id'), 'orders', ['order_id'], unique=False)
    
    op.create_table('order_items',
        sa.Column('order_item_id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('unit_price', sa.Float(), nullable=False),
        sa.Column('subtotal', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['order_id'], ['orders.order_id'], ),
        sa.ForeignKeyConstraint(['product_id'], ['products.product_id'], ),
        sa.PrimaryKeyConstraint('order_item_id')
    )
    op.create_index(op.f('ix_order_items_order_item_id'), 'order_items', ['order_item_id'], unique=False)
    
    op.create_table('cart_items',
        sa.Column('cart_item_id', sa.Integer(), nullable=False),
        sa.Column('cart_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['cart_id'], ['carts.cart_id'], ),
        sa.ForeignKeyConstraint(['product_id'], ['products.product_id'], ),
        sa.PrimaryKeyConstraint('cart_item_id')
    )
    op.create_index(op.f('ix_cart_items_cart_item_id'), 'cart_items', ['cart_item_id'], unique=False)
    
    op.create_table('payments',
        sa.Column('payment_id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('payment_method', sa.String(length=50), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('transaction_id', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['order_id'], ['orders.order_id'], ),
        sa.PrimaryKeyConstraint('payment_id')
    )
    op.create_index(op.f('ix_payments_payment_id'), 'payments', ['payment_id'], unique=False)
    
    op.create_table('reviews',
        sa.Column('review_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['product_id'], ['products.product_id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('review_id')
    )
    op.create_index(op.f('ix_reviews_review_id'), 'reviews', ['review_id'], unique=False)
    
    op.create_table('shipping',
        sa.Column('shipment_id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('courier_name', sa.String(length=100), nullable=False),
        sa.Column('tracking_number', sa.String(length=100), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('estimated_delivery', sa.DateTime(), nullable=True),
        sa.Column('delivered_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['order_id'], ['orders.order_id'], ),
        sa.PrimaryKeyConstraint('shipment_id')
    )
    op.create_index(op.f('ix_shipping_shipment_id'), 'shipping', ['shipment_id'], unique=False)


def downgrade():
    # Drop new tables
    op.drop_table('shipping')
    op.drop_table('reviews')
    op.drop_table('payments')
    op.drop_table('cart_items')
    op.drop_table('order_items')
    op.drop_table('orders')
    
    # Rename columns back to original names
    op.alter_column('carts', 'cart_id', new_column_name='id')
    op.alter_column('products', 'product_id', new_column_name='id')
    op.alter_column('categories', 'category_id', new_column_name='id')
    op.alter_column('users', 'phone', new_column_name='phone_number')
    op.alter_column('users', 'user_id', new_column_name='id')
