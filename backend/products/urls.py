"""
URL configuration for products app.

This module defines the complete URL routing structure for product-related
functionality in the BuyBuy e-commerce platform. It provides comprehensive
coverage of product catalog, cart management, and order processing workflows.

Features:
    - Product catalog browsing and management
    - Multi-vendor product CRUD operations
    - Shopping cart functionality
    - Complete order processing workflow
    - Sales tracking for vendors

Architecture:
    - Template-based views for user interface
    - RESTful URL patterns for intuitive navigation
    - Hierarchical organization by functionality
    - Namespace support for URL reversing

URL Patterns:
    Product Catalog:
        - '' : Product listing/catalog page
        - '<int:pk>/' : Individual product detail view
        - 'category/<int:category_id>/' : Products by category

    Product Management (Sellers):
        - 'add/' : Create new product
        - '<int:pk>/edit/' : Edit existing product
        - '<int:pk>/delete/' : Delete product
        - 'my-products/' : Seller's product dashboard

    Shopping Cart:
        - 'cart/' : View shopping cart contents
        - 'cart/add/<int:pk>/' : Add product to cart
        - 'cart/update/<int:pk>/' : Update cart item quantity
        - 'cart/remove/<int:pk>/' : Remove item from cart

    Order Processing:
        - 'checkout/' : Checkout and order creation
        - 'my-orders/' : Buyer's order history
        - 'order/<int:pk>/' : Individual order details
        - 'orders/<int:pk>/cancel/' : Cancel order functionality
        - 'my-sales/' : Seller's sales dashboard

Business Workflows Supported:
    1. Product Discovery:
       - Browse catalog → View categories → Product details

    2. Purchase Process:
       - Add to cart → View cart → Checkout → Order confirmation

    3. Seller Operations:
       - Add products → Manage inventory → Track sales

    4. Order Management:
       - View orders → Track status → Cancel if needed

Security Considerations:
    - Authentication required for all views (via @login_required decorators)
    - Object-level permissions enforced in views
    - CSRF protection for state-changing operations
    - URL parameter validation in view functions

Integration Points:
    - Links with categories app for product classification
    - Connects to authentication for user-specific operations
    - Integrates with template system for user interface
    - Supports future API endpoint extensions

Examples:
    Product browsing:
        - /products/ → All products list
        - /products/123/ → Product detail for ID 123
        - /products/category/5/ → Products in category 5

    Shopping workflow:
        - /products/cart/ → View cart
        - /products/checkout/ → Complete purchase
        - /products/my-orders/ → Order history

URL Namespace:
    - app_name = 'products' enables namespaced URL reversing
    - Usage: {% url 'products:product_detail' pk=123 %}
    - Prevents naming conflicts with other apps

Performance Considerations:
    - Integer primary key patterns for database efficiency
    - Hierarchical URL structure for logical navigation
    - Minimal parameter passing for faster routing

Notes:
    - All URLs require authentication (handled in views)
    - Supports both buyer and seller user types
    - Extensible design for additional functionality
    - Compatible with Django's URL reversing system
"""

from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Template views for frontend
    path('', views.product_list_view, name='product_list'),
    path('<int:pk>/', views.product_detail_view, name='product_detail'),
    path('add/', views.add_product_view, name='add_product'),
    path('<int:pk>/edit/', views.edit_product_view, name='edit_product'),
    path('<int:pk>/delete/', views.delete_product_view, name='delete_product'),
    path('my-products/', views.my_products_view, name='my_products'),
    path('category/<int:category_id>/', views.category_products_view, name='category_products'),

    # Cart functionality
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:pk>/', views.add_to_cart_view, name='add_to_cart'),
    path('cart/update/<int:pk>/', views.update_cart_item_view, name='update_cart_item'),
    path('cart/remove/<int:pk>/', views.remove_from_cart_view, name='remove_from_cart'),

    # Order functionality
    path('checkout/', views.checkout_view, name='checkout'),
    path('my-orders/', views.my_orders_view, name='my_orders'),
    path('order/<int:pk>/', views.order_detail_view, name='order_detail'),
    path('orders/<int:pk>/cancel/', views.cancel_order_view, name='cancel_order'),
    path('my-sales/', views.my_sales_view, name='my_sales'),
]
