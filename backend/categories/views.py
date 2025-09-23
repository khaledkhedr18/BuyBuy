"""
Category views for the BuyBuy e-commerce backend.
"""

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Category
from .serializers import CategorySerializer, CategoryTreeSerializer
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from categories.models import Category
from products.models import Product



@login_required
def categories_view(request):
    categories = Category.objects.all()
    return render(request, "categories.html", {"categories": categories})


class CategoryListView(generics.ListCreateAPIView):
    """
    List all categories or create a new category.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['parent', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'sort_order', 'created_at']
    ordering = ['sort_order', 'name']


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a category.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]


class CategoryCreateView(generics.CreateAPIView):
    """
    Create a new category.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]


class CategoryUpdateView(generics.UpdateAPIView):
    """
    Update a category.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]


class CategoryDeleteView(generics.DestroyAPIView):
    """
    Delete a category.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]


class CategoryTreeView(generics.ListAPIView):
    """
    Get category tree structure.
    """
    queryset = Category.objects.filter(parent=None, is_active=True)
    serializer_class = CategoryTreeSerializer
    permission_classes = [IsAuthenticated]


class CategoryChildrenView(generics.ListAPIView):
    """
    Get children of a specific category.
    """
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(
            parent_id=self.kwargs['pk'],
            is_active=True
        )


class CategoryProductListView(generics.ListAPIView):
    """
    Get products in a specific category.
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        from products.models import Product
        return Product.objects.filter(
            category_id=self.kwargs['pk'],
            is_active=True
        )

    def get_serializer_class(self):
        from products.serializers import ProductListSerializer
        return ProductListSerializer
