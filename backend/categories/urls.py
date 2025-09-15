"""
URL configuration for categories app.
"""

from django.urls import path
from . import views

app_name = 'categories'

urlpatterns = [
    # Category CRUD
    path('', views.CategoryListView.as_view(), name='category_list'),
    path('create/', views.CategoryCreateView.as_view(), name='category_create'),
    path('<int:pk>/', views.CategoryDetailView.as_view(), name='category_detail'),
    path('<int:pk>/update/', views.CategoryUpdateView.as_view(), name='category_update'),
    path('<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),

    # Category Hierarchy
    path('tree/', views.CategoryTreeView.as_view(), name='category_tree'),
    path('<int:pk>/children/', views.CategoryChildrenView.as_view(), name='category_children'),
    path('<int:pk>/products/', views.CategoryProductListView.as_view(), name='category_products'),
]
