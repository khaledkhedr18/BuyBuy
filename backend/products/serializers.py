"""
Product serializers for the BuyBuy e-commerce backend.
"""

from rest_framework import serializers
from .models import Product, ProductImage, ProductSpecification
from categories.models import Category


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for category information in products.
    """
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug')


class ProductImageSerializer(serializers.ModelSerializer):
    """
    Serializer for product images.
    """
    class Meta:
        model = ProductImage
        fields = ('id', 'image_url', 'alt_text', 'is_primary', 'sort_order', 'created_at')


class ProductSpecificationSerializer(serializers.ModelSerializer):
    """
    Serializer for product specifications.
    """
    class Meta:
        model = ProductSpecification
        fields = ('id', 'specification_name', 'specification_value', 'sort_order', 'created_at')


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for products.
    """
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    specifications = ProductSpecificationSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = (
            'id', 'name', 'description', 'short_description', 'sku', 'price',
            'compare_price', 'cost_price', 'category', 'category_id',
            'stock_quantity', 'low_stock_threshold', 'weight', 'dimensions',
            'is_active', 'is_featured', 'is_digital', 'requires_shipping',
            'tax_class', 'meta_title', 'meta_description', 'images',
            'specifications', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate_category_id(self, value):
        try:
            Category.objects.get(id=value)
        except Category.DoesNotExist:
            raise serializers.ValidationError("Category does not exist")
        return value


class ProductListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for product lists.
    """
    category = CategorySerializer(read_only=True)
    primary_image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'id', 'name', 'short_description', 'sku', 'price',
            'compare_price', 'category', 'stock_quantity',
            'is_active', 'is_featured', 'primary_image',
            'created_at'
        )

    def get_primary_image(self, obj):
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            return ProductImageSerializer(primary_image).data
        return None


class ProductCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating products.
    """
    class Meta:
        model = Product
        fields = (
            'name', 'description', 'short_description', 'sku', 'price',
            'compare_price', 'cost_price', 'category', 'stock_quantity',
            'low_stock_threshold', 'weight', 'dimensions', 'is_active',
            'is_featured', 'is_digital', 'requires_shipping', 'tax_class',
            'meta_title', 'meta_description'
        )

    def validate_sku(self, value):
        if Product.objects.filter(sku=value).exists():
            raise serializers.ValidationError("Product with this SKU already exists")
        return value
