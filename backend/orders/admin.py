"""
Admin configuration for orders app.
"""

from django.contrib import admin
from .models import Order, OrderItem, Cart, CartItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['seller']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'buyer', 'status', 'total_amount', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['buyer__username', 'buyer__email']
    inlines = [OrderItemInline]
    readonly_fields = ['total_amount']


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'get_items_count', 'get_total_price', 'updated_at']
    search_fields = ['user__username']
    inlines = [CartItemInline]