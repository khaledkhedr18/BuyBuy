"""
Category serializers for the BuyBuy e-commerce backend.
"""

from rest_framework import serializers
from .models import Category


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for categories.
    """
    product_count = serializers.ReadOnlyField()

    class Meta:
        model = Category
        fields = (
            'id', 'name', 'description', 'slug', 'parent', 'is_active',
            'sort_order', 'meta_title', 'meta_description', 'product_count',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'slug', 'created_at', 'updated_at')


class CategoryTreeSerializer(serializers.ModelSerializer):
    """
    Serializer for category tree structure.
    """
    children = serializers.SerializerMethodField()
    product_count = serializers.ReadOnlyField()

    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'children', 'product_count')

    def get_children(self, obj):
        children = obj.get_children()
        if children:
            return CategoryTreeSerializer(children, many=True).data
        return []


class CategoryCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating categories.
    """
    class Meta:
        model = Category
        fields = (
            'name', 'description', 'parent', 'is_active',
            'sort_order', 'meta_title', 'meta_description'
        )

    def validate_parent(self, value):
        if value and not value.is_active:
            raise serializers.ValidationError("Parent category must be active")
        return value


class CategoryDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for categories.
    """
    children = serializers.SerializerMethodField()
    ancestors = serializers.SerializerMethodField()
    product_count = serializers.ReadOnlyField()

    class Meta:
        model = Category
        fields = (
            'id', 'name', 'description', 'slug', 'parent', 'is_active',
            'sort_order', 'meta_title', 'meta_description', 'children',
            'ancestors', 'product_count', 'created_at', 'updated_at'
        )

    def get_children(self, obj):
        children = obj.get_children()
        if children:
            return CategorySerializer(children, many=True).data
        return []

    def get_ancestors(self, obj):
        ancestors = obj.get_ancestors()
        if ancestors:
            return CategorySerializer(ancestors, many=True).data
        return []
