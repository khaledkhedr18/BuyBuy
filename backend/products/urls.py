"""
URL configuration for products app.
"""

from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Template views for frontend
    path('', views.product_list_view, name='product_list'),
    path('<int:pk>/', views.product_detail_view, name='product_detail'),
    path('add/', views.add_product_view, name='add_product'),
    path('my-products/', views.my_products_view, name='my_products'),

    # Cart functionality
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:pk>/', views.add_to_cart_view, name='add_to_cart'),
    path('cart/update/<int:pk>/', views.update_cart_item_view, name='update_cart_item'),
    path('cart/remove/<int:pk>/', views.remove_from_cart_view, name='remove_from_cart'),

    # Order functionality
    path('checkout/', views.checkout_view, name='checkout'),
    path('my-orders/', views.my_orders_view, name='my_orders'),
    path('order/<int:pk>/', views.order_detail_view, name='order_detail'),
    path('my-sales/', views.my_sales_view, name='my_sales'),
]
