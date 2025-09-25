"""
URL configuration for the categories app in BuyBuy e-commerce backend.

This module defines URL patterns for category management functionality,
including both template-based views and REST API endpoints for comprehensive
category operations with hierarchical support.

URL Structure:
    - /categories/page/ - Template-based category listing page
    - /api/categories/ - REST API endpoints for category CRUD operations
    - /api/categories/tree/ - Hierarchical category tree structure
    - /api/categories/{id}/children/ - Child categories of specific parent
    - /api/categories/{id}/products/ - Products in specific category

Authentication:
    All API endpoints require authentication via JWT tokens or session authentication.
    Template views require login through Django's authentication system.

Examples:
    GET /categories/page/ -> Category management page (template)
    GET /api/categories/ -> List all categories (API)
    POST /api/categories/ -> Create new category (API)
    GET /api/categories/1/ -> Get specific category details (API)
    PUT /api/categories/1/ -> Update category (API)
    DELETE /api/categories/1/ -> Delete category (API)
    GET /api/categories/tree/ -> Get category hierarchy tree (API)
    GET /api/categories/1/children/ -> Get child categories (API)
    GET /api/categories/1/products/ -> Get products in category (API)
"""

from django.urls import path
from . import views

app_name = 'categories'

# URL patterns for category functionality
urlpatterns = [
    # Template-based views for frontend interface
    path(
        'page/',
        views.categories_view,
        name='categories'
    ),

    # REST API endpoints for category CRUD operations
    path(
        '',
        views.CategoryListView.as_view(),
        name='category_list'
    ),
    path(
        'create/',
        views.CategoryCreateView.as_view(),
        name='category_create'
    ),
    path(
        '<int:pk>/',
        views.CategoryDetailView.as_view(),
        name='category_detail'
    ),
    path(
        '<int:pk>/update/',
        views.CategoryUpdateView.as_view(),
        name='category_update'
    ),
    path(
        '<int:pk>/delete/',
        views.CategoryDeleteView.as_view(),
        name='category_delete'
    ),

    # Category hierarchy and navigation endpoints
    path(
        'tree/',
        views.CategoryTreeView.as_view(),
        name='category_tree'
    ),
    path(
        '<int:pk>/children/',
        views.CategoryChildrenView.as_view(),
        name='category_children'
    ),
    path(
        '<int:pk>/products/',
        views.CategoryProductListView.as_view(),
        name='category_products'
    ),
]
