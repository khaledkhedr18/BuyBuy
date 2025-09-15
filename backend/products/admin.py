"""
Admin configuration for products app.
"""

from django.contrib import admin
from .models import Product, ProductImage, ProductSpecification


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
    fields = ('specification_name', 'specification_value', 'sort_order')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Product admin configuration.
    """
    list_display = ('name', 'sku', 'category', 'price', 'stock_quantity', 'is_active', 'is_featured', 'created_at')
    list_filter = ('is_active', 'is_featured', 'is_digital', 'requires_shipping', 'category', 'created_at')
    search_fields = ('name', 'sku', 'description', 'short_description')
    ordering = ('-created_at',)

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'short_description', 'sku', 'category')
        }),
        ('Pricing', {
            'fields': ('price', 'compare_price', 'cost_price')
        }),
        ('Inventory', {
            'fields': ('stock_quantity', 'low_stock_threshold')
        }),
        ('Physical Properties', {
            'fields': ('weight', 'dimensions', 'requires_shipping')
        }),
        ('Status', {
            'fields': ('is_active', 'is_featured', 'is_digital')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
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
    list_display = ('product', 'specification_name', 'specification_value', 'sort_order', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('product__name', 'specification_name', 'specification_value')
    ordering = ('product', 'sort_order')
