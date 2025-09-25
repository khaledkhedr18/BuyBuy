"""
Category serializers for the BuyBuy e-commerce backend.

This module provides Django REST Framework serializers for category management
with comprehensive validation, hierarchy support, and optimized data handling.
"""

from rest_framework import serializers
from django.utils.text import slugify
from .models import Category


class CategorySerializer(serializers.ModelSerializer):
    """
    Standard serializer for category CRUD operations.

    This serializer handles basic category operations with validation
    for hierarchy integrity and business rules.

    Fields:
        id: Category unique identifier (read-only)
        name: Category display name (required, max 200 chars)
        description: Detailed category description (optional)
        slug: URL-friendly identifier (auto-generated, read-only)
        parent: Parent category ID for hierarchy (optional)
        is_active: Active status flag (default: True)
        sort_order: Display order within parent level (default: 0)
        meta_title: SEO page title (optional, max 200 chars)
        meta_description: SEO meta description (optional)
        product_count: Number of active products (read-only)
        created_at: Creation timestamp (read-only)
        updated_at: Last modification timestamp (read-only)

    Validation:
        - Prevents circular references in hierarchy
        - Validates parent category exists and is active
        - Ensures reasonable sort_order values
        - Auto-generates unique slugs from names
    """
    product_count = serializers.ReadOnlyField()
    full_path = serializers.CharField(source='full_path', read_only=True)
    depth_level = serializers.IntegerField(source='depth_level', read_only=True)

    class Meta:
        model = Category
        fields = (
            'id', 'name', 'description', 'slug', 'parent', 'is_active',
            'sort_order', 'meta_title', 'meta_description', 'product_count',
            'full_path', 'depth_level', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'slug', 'created_at', 'updated_at', 'product_count', 'full_path', 'depth_level')
        extra_kwargs = {
            'name': {'help_text': 'Display name for the category'},
            'description': {'help_text': 'Detailed description of the category'},
            'parent': {'help_text': 'Parent category for hierarchical organization'},
            'is_active': {'help_text': 'Whether this category is visible and usable'},
            'sort_order': {'help_text': 'Display order within the same parent level'},
            'meta_title': {'help_text': 'SEO page title for search engines'},
            'meta_description': {'help_text': 'SEO meta description for search engines'}
        }

    def validate_name(self, value):
        """
        Validate category name uniqueness within the same parent.

        Args:
            value (str): Category name to validate

        Returns:
            str: Validated and cleaned category name

        Raises:
            ValidationError: If name is empty or already exists in same parent
        """
        if not value or not value.strip():
            raise serializers.ValidationError("Category name cannot be empty.")

        value = value.strip()

        # Check for duplicate names in same parent during creation
        if not self.instance:  # Creating new category
            parent = self.initial_data.get('parent')
            existing = Category.objects.filter(
                name__iexact=value,
                parent_id=parent,
                is_active=True
            )
            if existing.exists():
                raise serializers.ValidationError(
                    "A category with this name already exists in the same parent category."
                )

        return value

    def validate_parent(self, value):
        """
        Validate parent category relationship.

        Args:
            value (Category or None): Parent category instance

        Returns:
            Category or None: Validated parent category

        Raises:
            ValidationError: If parent is invalid or would create circular reference
        """
        if value:
            # Check if parent is active
            if not value.is_active:
                raise serializers.ValidationError(
                    "Parent category must be active."
                )

            # Check for circular reference during update
            if self.instance and value:
                if value == self.instance:
                    raise serializers.ValidationError(
                        "Category cannot be its own parent."
                    )

                # Check if setting this parent would create a circular reference
                ancestors = value.get_ancestors()
                if self.instance in ancestors:
                    raise serializers.ValidationError(
                        "Cannot set parent: would create circular reference."
                    )

            # Check maximum nesting depth (5 levels: 0-4)
            if value.depth_level >= 4:
                raise serializers.ValidationError(
                    "Maximum category nesting depth (5 levels) would be exceeded."
                )

        return value

    def validate_sort_order(self, value):
        """
        Validate sort order value.

        Args:
            value (int): Sort order value

        Returns:
            int: Validated sort order

        Raises:
            ValidationError: If sort order is invalid
        """
        if value < 0:
            raise serializers.ValidationError("Sort order must be non-negative.")

        if value > 9999:
            raise serializers.ValidationError("Sort order must be 9999 or less.")

        return value

    def validate(self, attrs):
        """
        Cross-field validation for category data.

        Args:
            attrs (dict): All field data

        Returns:
            dict: Validated data

        Raises:
            ValidationError: If cross-field validation fails
        """
        # Validate SEO fields length if provided
        if attrs.get('meta_title') and len(attrs['meta_title']) > 200:
            raise serializers.ValidationError({
                'meta_title': 'SEO title must be 200 characters or less.'
            })

        if attrs.get('meta_description') and len(attrs['meta_description']) > 500:
            raise serializers.ValidationError({
                'meta_description': 'SEO description should be 500 characters or less for optimal results.'
            })

        return attrs


class CategoryTreeSerializer(serializers.ModelSerializer):
    """
    Serializer for hierarchical category tree representation.

    This serializer provides nested category data for building
    navigation trees and hierarchical displays.

    Fields:
        id: Category identifier
        name: Category name
        slug: URL-friendly identifier
        children: Nested child categories (recursive)
        product_count: Direct product count in category
        total_product_count: Product count including subcategories
        is_leaf: Whether category has no children

    Features:
        - Recursive serialization of category hierarchy
        - Optimized for tree rendering performance
        - Includes metadata useful for navigation
    """
    children = serializers.SerializerMethodField()
    product_count = serializers.ReadOnlyField()
    total_product_count = serializers.CharField(source='get_total_product_count', read_only=True)
    is_leaf = serializers.BooleanField(source='is_leaf', read_only=True)

    class Meta:
        model = Category
        fields = (
            'id', 'name', 'slug', 'sort_order', 'children',
            'product_count', 'total_product_count', 'is_leaf'
        )

    def get_children(self, obj):
        """
        Get serialized children for tree structure.

        Args:
            obj (Category): Category instance

        Returns:
            list: Serialized child categories or empty list
        """
        children = obj.get_children()
        if children:
            return CategoryTreeSerializer(children, many=True, context=self.context).data
        return []


class CategoryCreateSerializer(serializers.ModelSerializer):
    """
    Specialized serializer for creating categories with enhanced validation.

    This serializer focuses on category creation with comprehensive
    validation and automatic slug generation.

    Fields:
        name: Category name (required)
        description: Category description (optional)
        parent: Parent category (optional, validated)
        is_active: Active status (default: True)
        sort_order: Display order (default: 0)
        meta_title: SEO title (optional)
        meta_description: SEO description (optional)

    Features:
        - Enhanced validation for creation scenarios
        - Automatic slug generation with uniqueness checks
        - Business rule enforcement
    """

    class Meta:
        model = Category
        fields = (
            'name', 'description', 'parent', 'is_active',
            'sort_order', 'meta_title', 'meta_description'
        )
        extra_kwargs = {
            'name': {'required': True, 'help_text': 'Category name (required)'},
            'description': {'help_text': 'Detailed category description'},
            'parent': {'help_text': 'Parent category for hierarchy'},
            'sort_order': {'help_text': 'Display order (0-9999)'}
        }

    def validate_parent(self, value):
        """
        Validate parent category for creation.

        Args:
            value (Category or None): Parent category

        Returns:
            Category or None: Validated parent

        Raises:
            ValidationError: If parent is invalid
        """
        if value and not value.is_active:
            raise serializers.ValidationError(
                "Parent category must be active."
            )

        # Check nesting depth
        if value and value.depth_level >= 4:
            raise serializers.ValidationError(
                "Maximum category nesting depth would be exceeded."
            )

        return value

    def create(self, validated_data):
        """
        Create category with automatic slug generation.

        Args:
            validated_data (dict): Validated category data

        Returns:
            Category: Created category instance
        """
        # Generate unique slug
        name = validated_data['name']
        base_slug = slugify(name)
        slug = base_slug
        counter = 1

        while Category.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        validated_data['slug'] = slug
        return super().create(validated_data)


class CategoryDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for comprehensive category information.

    This serializer provides complete category data including
    relationships and computed properties for detailed views.

    Fields:
        All basic category fields plus:
        - children: Direct child categories
        - ancestors: Parent hierarchy path
        - breadcrumbs: Navigation breadcrumb data
        - statistics: Category usage statistics

    Features:
        - Complete relationship data
        - Navigation helpers
        - Performance statistics
        - Rich metadata for admin interfaces
    """
    children = serializers.SerializerMethodField()
    ancestors = serializers.SerializerMethodField()
    breadcrumbs = serializers.SerializerMethodField()
    statistics = serializers.SerializerMethodField()
    product_count = serializers.ReadOnlyField()
    full_path = serializers.CharField(source='full_path', read_only=True)
    depth_level = serializers.IntegerField(source='depth_level', read_only=True)
    is_leaf = serializers.BooleanField(source='is_leaf', read_only=True)
    can_be_deleted = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = (
            'id', 'name', 'description', 'slug', 'parent', 'is_active',
            'sort_order', 'meta_title', 'meta_description', 'children',
            'ancestors', 'breadcrumbs', 'statistics', 'product_count',
            'full_path', 'depth_level', 'is_leaf', 'can_be_deleted',
            'created_at', 'updated_at'
        )

    def get_children(self, obj):
        """
        Get direct child categories.

        Args:
            obj (Category): Category instance

        Returns:
            list: Serialized child categories
        """
        children = obj.get_children()
        if children:
            return CategorySerializer(children, many=True, context=self.context).data
        return []

    def get_ancestors(self, obj):
        """
        Get ancestor categories for breadcrumb navigation.

        Args:
            obj (Category): Category instance

        Returns:
            list: Serialized ancestor categories from root to parent
        """
        ancestors = obj.get_ancestors()
        if ancestors:
            # Reverse to show from root to immediate parent
            return CategorySerializer(
                reversed(ancestors),
                many=True,
                context=self.context
            ).data
        return []

    def get_breadcrumbs(self, obj):
        """
        Get breadcrumb navigation data.

        Args:
            obj (Category): Category instance

        Returns:
            list: Breadcrumb items with name and slug
        """
        breadcrumbs = []
        ancestors = obj.get_ancestors()

        # Add ancestors (reversed to go from root to parent)
        for ancestor in reversed(ancestors):
            breadcrumbs.append({
                'id': ancestor.id,
                'name': ancestor.name,
                'slug': ancestor.slug
            })

        # Add current category
        breadcrumbs.append({
            'id': obj.id,
            'name': obj.name,
            'slug': obj.slug,
            'is_current': True
        })

        return breadcrumbs

    def get_statistics(self, obj):
        """
        Get category usage statistics.

        Args:
            obj (Category): Category instance

        Returns:
            dict: Statistics about category usage
        """
        return {
            'direct_products': obj.product_count,
            'total_products': obj.get_total_product_count(),
            'direct_children': obj.get_children().count(),
            'total_descendants': len(obj.get_descendants()),
            'depth_level': obj.depth_level,
            'is_root': obj.parent is None,
            'is_leaf': obj.is_leaf
        }

    def get_can_be_deleted(self, obj):
        """
        Get deletion status information.

        Args:
            obj (Category): Category instance

        Returns:
            dict: Deletion status and reason
        """
        can_delete, reason = obj.can_be_deleted()
        return {
            'can_delete': can_delete,
            'reason': reason
        }


class CategoryUpdateSerializer(serializers.ModelSerializer):
    """
    Specialized serializer for updating categories with validation.

    This serializer handles category updates with enhanced validation
    to maintain hierarchy integrity and business rules.

    Fields:
        All editable category fields with appropriate validation

    Features:
        - Hierarchy change validation
        - Prevents data inconsistencies
        - Maintains referential integrity
    """

    class Meta:
        model = Category
        fields = (
            'name', 'description', 'parent', 'is_active',
            'sort_order', 'meta_title', 'meta_description'
        )
        extra_kwargs = {
            'name': {'help_text': 'Category display name'},
            'parent': {'help_text': 'Parent category (validate hierarchy)'}
        }

    def validate_parent(self, value):
        """
        Validate parent change for updates.

        Args:
            value (Category or None): New parent category

        Returns:
            Category or None: Validated parent

        Raises:
            ValidationError: If parent change is invalid
        """
        if value and self.instance:
            # Prevent self-parenting
            if value == self.instance:
                raise serializers.ValidationError(
                    "Category cannot be its own parent."
                )

            # Prevent circular references
            if self.instance in value.get_ancestors():
                raise serializers.ValidationError(
                    "Cannot set parent: would create circular reference."
                )

            # Check if parent is active
            if not value.is_active:
                raise serializers.ValidationError(
                    "Parent category must be active."
                )

            # Check nesting depth
            if value.depth_level >= 4:
                raise serializers.ValidationError(
                    "Maximum category nesting depth would be exceeded."
                )

        return value

    def update(self, instance, validated_data):
        """
        Update category with validation and slug regeneration if needed.

        Args:
            instance (Category): Category instance to update
            validated_data (dict): Validated update data

        Returns:
            Category: Updated category instance
        """
        # Regenerate slug if name changed
        if 'name' in validated_data and validated_data['name'] != instance.name:
            base_slug = slugify(validated_data['name'])
            slug = base_slug
            counter = 1

            while Category.objects.filter(slug=slug).exclude(pk=instance.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            validated_data['slug'] = slug

        return super().update(instance, validated_data)
