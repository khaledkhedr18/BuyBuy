"""
Admin configuration for products app.
"""

from django.contrib import admin
from .models import Product, ProductImage, ProductSpecification, Cart, CartItem, Order, OrderItem


class ProductImageInline(admin.TabularInline):
    """
    Inline admin for product images.
    """
    model = ProductImage
    extra = 1
    fields = ('image_url', 'alt_text', 'is_primary', 'sort_order')


class ProductSpecificationInline(admin.TabularInline):
    """
    Inline admin for product specifications.
    """
    model = ProductSpecification
    extra = 1
    fields = ('name', 'value')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Product admin configuration.
    """
    list_display = ('name', 'category', 'price', 'stock_quantity', 'seller', 'is_active', 'created_at')
    list_filter = ('is_active', 'category', 'created_at', 'seller')
    search_fields = ('name', 'description', 'short_description')
    ordering = ('-created_at',)

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'short_description', 'category', 'seller')
        }),
        ('Pricing & Inventory', {
            'fields': ('price', 'stock_quantity')
        }),
        ('Media', {
            'fields': ('image_url',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('created_at', 'updated_at')
    inlines = [ProductImageInline, ProductSpecificationInline]


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    """
    Product Image admin configuration.
    """
    list_display = ('product', 'image_url', 'is_primary', 'sort_order', 'created_at')
    list_filter = ('is_primary', 'created_at')
    search_fields = ('product__name', 'alt_text')
    ordering = ('product', 'sort_order')


@admin.register(ProductSpecification)
class ProductSpecificationAdmin(admin.ModelAdmin):
    """
    Product Specification admin configuration.
    """
    list_display = ('product', 'name', 'value', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('product__name', 'name', 'value')
    ordering = ('product', 'name')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """
    Cart admin configuration.
    """
    list_display = ('user', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__username', 'user__email')


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """
    Cart Item admin configuration.
    """
    list_display = ('cart', 'product', 'quantity', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('cart__user__username', 'product__name')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Order admin configuration.
    """
    list_display = ('buyer', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('buyer__username', 'buyer__email')
    ordering = ('-created_at',)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """
    Order Item admin configuration.
    """
    list_display = ('order', 'product', 'seller', 'quantity', 'price', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('order__buyer__username', 'product__name', 'seller__username')
