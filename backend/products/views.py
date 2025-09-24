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
from django.contrib.auth.decorators import login_required

from django.shortcuts import render

def products_view(request):
    """Display products with e-commerce functionality."""
    products = Product.objects.filter(is_active=True).order_by('-created_at')
    categories = None
    
    # Import here to avoid circular imports
    try:
        from categories.models import Category
        categories = Category.objects.filter(is_active=True)
    except ImportError:
        pass
    
    return render(request, "products.html", {
        "products": products,
        "categories": categories
    })


@login_required
def seller_products_view(request):
    """Display seller's own products."""
    products = Product.objects.filter(seller=request.user).order_by('-created_at')
    categories = None
    
    # Import here to avoid circular imports
    try:
        from categories.models import Category
        categories = Category.objects.filter(is_active=True)
    except ImportError:
        pass
    
    return render(request, "seller_products.html", {
        "products": products,
        "categories": categories
    })


@login_required 
def seller_orders_view(request):
    """Display seller's received orders dashboard."""
    # Import here to avoid circular imports
    from orders.models import OrderItem
    
    # Get all order items where the seller is the current user
    order_items = OrderItem.objects.filter(
        seller=request.user
    ).select_related('order', 'product').order_by('-order__created_at')
    
    # Group by orders for better presentation
    orders_data = []
    orders_dict = {}
    total_revenue = 0
    total_items_sold = 0
    pending_orders = 0
    
    for item in order_items:
        order_id = item.order.id
        if order_id not in orders_dict:
            order_data = {
                'order_id': order_id,
                'buyer': item.order.buyer.username,
                'buyer_email': item.order.buyer.email,
                'status': item.order.status,
                'total_amount': item.order.total_amount,
                'created_at': item.order.created_at,
                'shipping_address': item.order.shipping_address,
                'items': []
            }
            orders_dict[order_id] = order_data
            orders_data.append(order_data)
            
            if item.order.status == 'pending':
                pending_orders += 1
        
        orders_dict[order_id]['items'].append({
            'product_name': item.product.name,
            'quantity': item.quantity,
            'price': item.price,
            'total_price': item.get_total_price()
        })
        
        total_revenue += float(item.get_total_price())
        total_items_sold += item.quantity
    
    context = {
        'orders': orders_data,
        'total_orders': len(orders_data),
        'total_revenue': total_revenue,
        'pending_orders': pending_orders,
        'total_items_sold': total_items_sold
    }
    
    return render(request, "seller_orders.html", context)
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

    def get_queryset(self):
        """Allow sellers to only access their own products for modifications."""
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return Product.objects.filter(seller=self.request.user)
        return Product.objects.all()


class ProductCreateView(generics.CreateAPIView):
    """
    Create a new product.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """Automatically set the seller to the current user."""
        serializer.save(seller=self.request.user)


class ProductUpdateView(generics.UpdateAPIView):
    """
    Update a product.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Allow sellers to only update their own products."""
        return Product.objects.filter(seller=self.request.user)


class ProductDeleteView(generics.DestroyAPIView):
    """
    Delete a product.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Allow sellers to only delete their own products."""
        return Product.objects.filter(seller=self.request.user)


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


class SellerProductListView(generics.ListAPIView):
    """
    List products owned by the current seller.
    """
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Product.objects.filter(seller=self.request.user).order_by('-created_at')


class SellerOrderDashboardView(generics.ListAPIView):
    """
    List orders received by the current seller for their products.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Import here to avoid circular imports
        from orders.models import OrderItem
        from orders.serializers import OrderItemSerializer
        
        # Get all order items where the seller is the current user
        order_items = OrderItem.objects.filter(
            seller=request.user
        ).select_related('order', 'product').order_by('-order__created_at')
        
        # Group by orders for better presentation
        orders_data = {}
        for item in order_items:
            order_id = item.order.id
            if order_id not in orders_data:
                orders_data[order_id] = {
                    'order_id': order_id,
                    'buyer': item.order.buyer.username,
                    'buyer_email': item.order.buyer.email,
                    'status': item.order.status,
                    'total_amount': str(item.order.total_amount),
                    'created_at': item.order.created_at,
                    'shipping_address': item.order.shipping_address,
                    'items': []
                }
            
            orders_data[order_id]['items'].append({
                'product_id': item.product.id,
                'product_name': item.product.name,
                'quantity': item.quantity,
                'price': str(item.price),
                'total_price': str(item.get_total_price())
            })
        
        return Response({
            'success': True,
            'data': list(orders_data.values())
        })
