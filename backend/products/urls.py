"""
URL configuration for products app.
"""

from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Product CRUD
    # Template view for frontend Products page
    path('page/', views.products_view, name='products'),
    
    # Seller template views
    path('seller/products/', views.seller_products_view, name='seller_products_page'),
    path('seller/orders/', views.seller_orders_view, name='seller_orders_page'),

    # API endpoints
    path('', views.ProductListView.as_view(), name='product_list'),
    path('create/', views.ProductCreateView.as_view(), name='product_create'),
    path('<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('<int:pk>/update/', views.ProductUpdateView.as_view(), name='product_update'),
    path('<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),
    # Product Images
    path('<int:pk>/images/', views.ProductImageView.as_view(), name='product_images'),
    path('<int:pk>/images/upload/', views.ProductImageUploadView.as_view(), name='product_image_upload'),
    path('images/<int:pk>/delete/', views.ProductImageDeleteView.as_view(), name='product_image_delete'),

    # Product Specifications
    path('<int:pk>/specifications/', views.ProductSpecificationView.as_view(), name='product_specifications'),
    path('<int:pk>/specifications/create/', views.ProductSpecificationCreateView.as_view(), name='product_specification_create'),
    path('specifications/<int:pk>/update/', views.ProductSpecificationUpdateView.as_view(), name='product_specification_update'),
    path('specifications/<int:pk>/delete/', views.ProductSpecificationDeleteView.as_view(), name='product_specification_delete'),

    # Product Search and Filtering
    path('search/', views.ProductSearchView.as_view(), name='product_search'),
    path('featured/', views.FeaturedProductListView.as_view(), name='featured_products'),
    path('low-stock/', views.LowStockProductListView.as_view(), name='low_stock_products'),
    
    # Seller-specific endpoints
    path('my-products/', views.SellerProductListView.as_view(), name='seller_products'),
    path('my-orders/', views.SellerOrderDashboardView.as_view(), name='seller_orders'),
]
