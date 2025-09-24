"""
Order serializers for the BuyBuy e-commerce backend.
"""

from rest_framework import serializers
from .models import Order, OrderItem, Cart, CartItem
from products.serializers import ProductListSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Serializer for order items.
    """
    product = ProductListSerializer(read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'quantity', 'price', 'seller')


class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for orders.
    """
    items = OrderItemSerializer(many=True, read_only=True)
    buyer_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = ('id', 'buyer', 'buyer_name', 'status', 'total_amount', 
                 'shipping_address', 'created_at', 'updated_at', 'items')
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def get_buyer_name(self, obj):
        return f"{obj.buyer.first_name} {obj.buyer.last_name}".strip() or obj.buyer.username


class CartItemSerializer(serializers.ModelSerializer):
    """
    Serializer for cart items.
    """
    product = ProductListSerializer(read_only=True)
    total_price = serializers.SerializerMethodField()
    
    class Meta:
        model = CartItem
        fields = ('id', 'product', 'quantity', 'total_price')
    
    def get_total_price(self, obj):
        return obj.get_total_price()


class CartSerializer(serializers.ModelSerializer):
    """
    Serializer for shopping carts.
    """
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    items_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = ('id', 'user', 'items', 'total_price', 'items_count', 
                 'created_at', 'updated_at')
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')
    
    def get_total_price(self, obj):
        return obj.get_total_price()
    
    def get_items_count(self, obj):
        return obj.get_items_count()