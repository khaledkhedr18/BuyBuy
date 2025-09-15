"""
Product views for the BuyBuy e-commerce backend.
"""

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db import models
from .models import Product, ProductImage, ProductSpecification
from .serializers import ProductSerializer, ProductImageSerializer, ProductSpecificationSerializer


class ProductListView(generics.ListCreateAPIView):
    """
    List all products or create a new product.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'is_active', 'is_featured']
    search_fields = ['name', 'description', 'short_description']
    ordering_fields = ['name', 'price', 'created_at', 'updated_at']
    ordering = ['-created_at']


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a product.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]


class ProductCreateView(generics.CreateAPIView):
    """
    Create a new product.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]


class ProductUpdateView(generics.UpdateAPIView):
    """
    Update a product.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]


class ProductDeleteView(generics.DestroyAPIView):
    """
    Delete a product.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]


class ProductImageView(generics.ListCreateAPIView):
    """
    List or create product images.
    """
    serializer_class = ProductImageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ProductImage.objects.filter(product_id=self.kwargs['pk'])


class ProductImageUploadView(generics.CreateAPIView):
    """
    Upload product images.
    """
    serializer_class = ProductImageSerializer
    permission_classes = [IsAuthenticated]


class ProductImageDeleteView(generics.DestroyAPIView):
    """
    Delete a product image.
    """
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    permission_classes = [IsAuthenticated]


class ProductSpecificationView(generics.ListCreateAPIView):
    """
    List or create product specifications.
    """
    serializer_class = ProductSpecificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ProductSpecification.objects.filter(product_id=self.kwargs['pk'])


class ProductSpecificationCreateView(generics.CreateAPIView):
    """
    Create product specification.
    """
    serializer_class = ProductSpecificationSerializer
    permission_classes = [IsAuthenticated]


class ProductSpecificationUpdateView(generics.UpdateAPIView):
    """
    Update product specification.
    """
    queryset = ProductSpecification.objects.all()
    serializer_class = ProductSpecificationSerializer
    permission_classes = [IsAuthenticated]


class ProductSpecificationDeleteView(generics.DestroyAPIView):
    """
    Delete product specification.
    """
    queryset = ProductSpecification.objects.all()
    serializer_class = ProductSpecificationSerializer
    permission_classes = [IsAuthenticated]


class ProductSearchView(generics.ListAPIView):
    """
    Search products.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ['name', 'description', 'short_description']


class FeaturedProductListView(generics.ListAPIView):
    """
    List featured products.
    """
    queryset = Product.objects.filter(is_featured=True, is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]


class LowStockProductListView(generics.ListAPIView):
    """
    List products with low stock.
    """
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Product.objects.filter(
            is_active=True,
            stock_quantity__lte=models.F('low_stock_threshold')
        )
