"""
Category views for the BuyBuy e-commerce backend.

This module provides both template-based views for the frontend interface
and REST API views for programmatic access to category management.
"""

from rest_framework import generics, status, serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.contrib import messages

from .models import Category
from .serializers import CategorySerializer, CategoryTreeSerializer
from products.models import Product


@login_required
def categories_view(request):
    """
    Display categories page with hierarchical category listing.

    This view renders the categories template with all active categories
    organized in a hierarchical structure for easy navigation and management.

    Args:
        request (HttpRequest): The HTTP request object containing user session

    Returns:
        HttpResponse: Rendered categories.html template with context data

    Context:
        categories: QuerySet of all Category objects ordered by sort_order and name
        root_categories: QuerySet of root-level categories for tree navigation
        total_categories: Total count of active categories

    Example:
        GET /categories/ -> Returns categories page with navigation tree
    """
    try:
        # Get all categories with related data for efficient rendering
        categories = Category.objects.select_related('parent').prefetch_related('children')
        root_categories = Category.objects.get_root_categories()

        context = {
            'categories': categories,
            'root_categories': root_categories,
            'total_categories': categories.filter(is_active=True).count(),
            'page_title': 'Product Categories',
        }

        return render(request, "categories.html", context)

    except Exception as e:
        messages.error(request, f"Error loading categories: {str(e)}")
        return render(request, "categories.html", {'categories': []})


class CategoryListView(generics.ListCreateAPIView):
    """
    API view for listing all categories and creating new categories.

    This view provides paginated listing of categories with filtering, searching,
    and ordering capabilities. Authenticated users can create new categories.

    Permissions:
        - GET: Requires authentication
        - POST: Requires authentication

    Filtering:
        - parent: Filter by parent category ID
        - is_active: Filter by active status (true/false)

    Searching:
        - Search in name and description fields

    Ordering:
        - Available fields: name, sort_order, created_at
        - Default: sort_order, name

    Examples:
        GET /api/categories/ -> List all categories
        GET /api/categories/?parent=1 -> List subcategories of category 1
        GET /api/categories/?search=electronics -> Search categories containing 'electronics'
        POST /api/categories/ -> Create new category
    """
    queryset = Category.objects.select_related('parent').prefetch_related('children')
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['parent', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'sort_order', 'created_at']
    ordering = ['sort_order', 'name']

    def get_queryset(self):
        """
        Customize queryset based on request parameters.

        Returns:
            QuerySet: Filtered and optimized category queryset
        """
        queryset = super().get_queryset()

        # Filter by active status if not explicitly filtering
        if 'is_active' not in self.request.GET:
            queryset = queryset.filter(is_active=True)

        return queryset

    def perform_create(self, serializer):
        """
        Handle category creation with additional validation.

        Args:
            serializer (CategorySerializer): Validated serializer instance
        """
        # Additional business logic can be added here
        serializer.save()


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, or deleting a specific category.

    This view provides full CRUD operations for individual categories
    with proper authorization and validation.

    Permissions:
        - GET: Requires authentication
        - PUT/PATCH: Requires authentication
        - DELETE: Requires authentication (with additional validation)

    Examples:
        GET /api/categories/1/ -> Get category details
        PUT /api/categories/1/ -> Update entire category
        PATCH /api/categories/1/ -> Partial category update
        DELETE /api/categories/1/ -> Delete category (if allowed)
    """
    queryset = Category.objects.select_related('parent').prefetch_related('children')
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def perform_destroy(self, instance):
        """
        Handle category deletion with business rule validation.

        Args:
            instance (Category): Category instance to be deleted

        Raises:
            ValidationError: If category cannot be safely deleted
        """
        can_delete, reason = instance.can_be_deleted()
        if not can_delete:
            return Response(
                {'error': reason},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Soft delete by setting is_active=False instead of hard delete
        instance.is_active = False
        instance.save(update_fields=['is_active', 'updated_at'])


class CategoryCreateView(generics.CreateAPIView):
    """
    API view dedicated to creating new categories.

    This specialized view handles category creation with enhanced
    validation and business logic for category hierarchy management.

    Permissions:
        - POST: Requires authentication

    Validation:
        - Prevents circular references in category hierarchy
        - Validates maximum nesting depth
        - Ensures parent category is active

    Examples:
        POST /api/categories/create/ -> Create new category with validation
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """
        Create category with additional validation and business logic.

        Args:
            serializer (CategorySerializer): Validated serializer instance
        """
        # Validate parent category if provided
        parent = serializer.validated_data.get('parent')
        if parent:
            if not parent.is_active:
                raise serializers.ValidationError(
                    "Parent category must be active"
                )
            if parent.depth_level >= 4:  # Max 5 levels (0-4)
                raise serializers.ValidationError(
                    "Maximum category nesting depth exceeded"
                )

        serializer.save()


class CategoryUpdateView(generics.UpdateAPIView):
    """
    API view dedicated to updating existing categories.

    This view handles category updates with validation to maintain
    hierarchy integrity and business rules.

    Permissions:
        - PUT/PATCH: Requires authentication

    Validation:
        - Prevents moving category to create circular references
        - Validates hierarchy depth limits
        - Ensures data consistency

    Examples:
        PUT /api/categories/1/update/ -> Full category update
        PATCH /api/categories/1/update/ -> Partial category update
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        """
        Update category with hierarchy validation.

        Args:
            serializer (CategorySerializer): Validated serializer instance
        """
        # Validate parent change if applicable
        if 'parent' in serializer.validated_data:
            new_parent = serializer.validated_data['parent']
            instance = self.get_object()

            if new_parent and new_parent != instance.parent:
                # Check for circular references
                if new_parent == instance or instance in new_parent.get_ancestors():
                    raise serializers.ValidationError(
                        "Cannot set parent: would create circular reference"
                    )

        serializer.save()


class CategoryDeleteView(generics.DestroyAPIView):
    """
    API view dedicated to deleting categories.

    This view handles category deletion with comprehensive validation
    to ensure data integrity and prevent orphaned products.

    Permissions:
        - DELETE: Requires authentication

    Validation:
        - Checks for associated active products
        - Checks for active subcategories
        - Provides detailed error messages

    Examples:
        DELETE /api/categories/1/delete/ -> Delete category if allowed
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def perform_destroy(self, instance):
        """
        Delete category with comprehensive validation.

        Args:
            instance (Category): Category instance to delete

        Returns:
            Response: Success or error response
        """
        can_delete, reason = instance.can_be_deleted()
        if not can_delete:
            return Response(
                {'error': reason, 'can_delete': False},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Perform soft delete to maintain referential integrity
        instance.is_active = False
        instance.save(update_fields=['is_active', 'updated_at'])


class CategoryTreeView(generics.ListAPIView):
    """
    API view for retrieving hierarchical category tree structure.

    This view returns categories organized in a tree structure starting
    from root categories, useful for navigation menus and category browsing.

    Permissions:
        - GET: Requires authentication

    Response Format:
        Returns nested category objects with children arrays for tree rendering

    Examples:
        GET /api/categories/tree/ -> Get complete category hierarchy
    """
    queryset = Category.objects.filter(parent=None, is_active=True).order_by('sort_order', 'name')
    serializer_class = CategoryTreeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Optimize queryset for tree structure retrieval.

        Returns:
            QuerySet: Root categories with prefetched children for efficient tree building
        """
        return super().get_queryset().prefetch_related(
            'children',
            'children__children',
            'children__children__children'
        )


class CategoryChildrenView(generics.ListAPIView):
    """
    API view for retrieving children of a specific category.

    This view returns direct child categories of a given parent category,
    useful for dynamic category loading and navigation.

    Permissions:
        - GET: Requires authentication

    URL Parameters:
        pk: Parent category ID

    Examples:
        GET /api/categories/1/children/ -> Get children of category 1
    """
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Get active children of the specified parent category.

        Returns:
            QuerySet: Active child categories ordered by sort_order and name
        """
        parent_id = self.kwargs.get('pk')
        return Category.objects.filter(
            parent_id=parent_id,
            is_active=True
        ).order_by('sort_order', 'name')

    def list(self, request, *args, **kwargs):
        """
        List children with additional metadata.

        Args:
            request (Request): HTTP request object
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments

        Returns:
            Response: Serialized children with parent information
        """
        parent_id = self.kwargs.get('pk')

        try:
            parent = Category.objects.get(pk=parent_id, is_active=True)
        except Category.DoesNotExist:
            return Response(
                {'error': 'Parent category not found or inactive'},
                status=status.HTTP_404_NOT_FOUND
            )

        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        return Response({
            'parent': {
                'id': parent.id,
                'name': parent.name,
                'full_path': parent.full_path
            },
            'children': serializer.data,
            'children_count': queryset.count()
        })


class CategoryProductListView(generics.ListAPIView):
    """
    API view for retrieving products in a specific category.

    This view returns paginated list of active products belonging to
    a specific category, with filtering and ordering options.

    Permissions:
        - GET: Requires authentication

    URL Parameters:
        pk: Category ID

    Query Parameters:
        include_subcategories: Include products from subcategories (default: false)

    Examples:
        GET /api/categories/1/products/ -> Get products in category 1
        GET /api/categories/1/products/?include_subcategories=true -> Include subcategory products
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'price', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        Get products for the specified category.

        Returns:
            QuerySet: Active products in the category (and subcategories if requested)
        """
        from products.models import Product

        category_id = self.kwargs.get('pk')
        include_subcategories = self.request.query_params.get('include_subcategories', 'false').lower() == 'true'

        try:
            category = Category.objects.get(pk=category_id, is_active=True)
        except Category.DoesNotExist:
            return Product.objects.none()

        if include_subcategories:
            # Get products from this category and all its descendants
            descendant_ids = [cat.id for cat in category.get_descendants()]
            category_ids = [category.id] + descendant_ids
            return Product.objects.filter(
                category_id__in=category_ids,
                is_active=True
            ).select_related('category', 'seller')
        else:
            return Product.objects.filter(
                category=category,
                is_active=True
            ).select_related('category', 'seller')

    def get_serializer_class(self):
        """
        Get appropriate serializer for product listing.

        Returns:
            Serializer: ProductListSerializer for efficient product listing
        """
        from products.serializers import ProductListSerializer
        return ProductListSerializer

    def list(self, request, *args, **kwargs):
        """
        List products with category context.

        Args:
            request (Request): HTTP request object
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments

        Returns:
            Response: Paginated product list with category information
        """
        category_id = self.kwargs.get('pk')

        try:
            category = Category.objects.get(pk=category_id, is_active=True)
        except Category.DoesNotExist:
            return Response(
                {'error': 'Category not found or inactive'},
                status=status.HTTP_404_NOT_FOUND
            )

        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response_data = self.get_paginated_response(serializer.data).data

            # Add category context
            response_data['category'] = {
                'id': category.id,
                'name': category.name,
                'full_path': category.full_path,
                'total_products': category.get_total_product_count()
            }
            return Response(response_data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'category': {
                'id': category.id,
                'name': category.name,
                'full_path': category.full_path,
                'total_products': category.get_total_product_count()
            },
            'products': serializer.data,
            'count': queryset.count()
        })
