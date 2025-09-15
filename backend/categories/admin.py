"""
Admin configuration for categories app.
"""

from django.contrib import admin
from .models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Category admin configuration.
    """
    list_display = ('name', 'parent', 'is_active', 'sort_order', 'product_count', 'created_at')
    list_filter = ('is_active', 'parent', 'created_at')
    search_fields = ('name', 'description', 'slug')
    ordering = ('sort_order', 'name')

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'slug', 'parent')
        }),
        ('Status', {
            'fields': ('is_active', 'sort_order')
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

    def product_count(self, obj):
        """Display the number of products in this category."""
        return obj.product_count
    product_count.short_description = 'Products'
