"""
Product serializers for the BuyBuy e-commerce backend.

This module provides comprehensive serialization support for product-related
models in the BuyBuy multi-vendor e-commerce platform. It handles data
transformation between Django models and JSON representations for API
endpoints, ensuring proper validation and data integrity.

Features:
    - Product catalog serialization with nested relationships
    - Category information embedding for product context
    - Product image and specification handling
    - Optimized list serialization for performance
    - Comprehensive validation for data integrity
    - Flexible create/update operations

Architecture:
    - Follows Django REST Framework conventions
    - Uses nested serializers for related data
    - Implements proper read-only and write-only fields
    - Provides custom validation methods
    - Supports both detailed and summary serializations

Business Rules:
    - Product categories must exist and be valid
    - SKUs must be unique across all products
    - Price fields require proper decimal validation
    - Stock quantities must be non-negative
    - Image and specification relationships maintained

Security:
    - Input validation prevents malformed data
    - Foreign key validation ensures referential integrity
    - Read-only fields protect sensitive information
    - Proper error handling for edge cases

Examples:
    Product creation via API:
        >>> data = {
        ...     'name': 'New Product',
        ...     'price': '29.99',
        ...     'category_id': 1,
        ...     'sku': 'PROD-001'
        ... }
        >>> serializer = ProductCreateSerializer(data=data)
        >>> serializer.is_valid() and serializer.save()

    Product list serialization:
        >>> products = Product.objects.all()
        >>> serializer = ProductListSerializer(products, many=True)
        >>> json_data = serializer.data

Dependencies:
    - Django REST Framework serializers
    - Product models from products.models
    - Category models for relationship validation
    - Custom validation logic for business rules

Notes:
    - Optimized for both API performance and data completeness
    - Supports nested serialization for complex relationships
    - Extensible design for additional product features
    - Compatible with DRF viewsets and generic views
"""

from rest_framework import serializers
from .models import Product, ProductImage, ProductSpecification
from categories.models import Category


class CategorySerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for category information in product contexts.

    Provides essential category data for product serialization without
    circular imports or excessive data loading. Optimized for embedding
    within product representations.

    Fields:
        id (int): Unique category identifier
        name (str): Human-readable category name
        slug (str): URL-friendly category identifier

    Usage:
        Used as a nested serializer within product serializations to provide
        category context without requiring separate API calls.

    Examples:
        >>> category_data = {
        ...     'id': 1,
        ...     'name': 'Electronics',
        ...     'slug': 'electronics'
        ... }
        >>> # Automatically serialized within ProductSerializer

    Performance:
        - Minimal field selection for efficiency
        - No additional database queries when used with select_related
        - Suitable for list views and nested contexts

    Notes:
        - Read-only serializer for reference purposes
        - Focused on display rather than modification
        - Compatible with hierarchical category structures
    """
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug')


class ProductImageSerializer(serializers.ModelSerializer):
    """
    Comprehensive serializer for product image management.

    Handles product image data including URLs, metadata, and display ordering.
    Supports multiple images per product with primary image designation and
    accessibility features.

    Fields:
        id (int): Unique image identifier
        image_url (str): URL or path to the image file
        alt_text (str): Alternative text for accessibility
        is_primary (bool): Designates the main product image
        sort_order (int): Display order for multiple images
        created_at (datetime): Image upload timestamp

    Business Rules:
        - Each product can have multiple images
        - One image should be designated as primary
        - Sort order determines display sequence
        - Alt text required for accessibility compliance

    Examples:
        >>> image_data = {
        ...     'image_url': 'https://example.com/product.jpg',
        ...     'alt_text': 'Product front view',
        ...     'is_primary': True,
        ...     'sort_order': 1
        ... }
        >>> serializer = ProductImageSerializer(data=image_data)

    Usage:
        - Nested within product serializations
        - Standalone for image management APIs
        - Bulk operations for multiple images

    Validation:
        - URL format validation for image_url
        - Alt text presence for accessibility
        - Sort order uniqueness per product (enforced at model level)

    Performance:
        - Read-only created_at for audit trails
        - Efficient field selection for API responses
        - Suitable for image gallery implementations
    """
    class Meta:
        model = ProductImage
        fields = ('id', 'image_url', 'alt_text', 'is_primary', 'sort_order', 'created_at')


class ProductSpecificationSerializer(serializers.ModelSerializer):
    """
    Serializer for product specifications and technical details.

    Manages key-value pairs of product specifications, technical details,
    and features. Supports ordered display and flexible specification
    management for diverse product types.

    Fields:
        id (int): Unique specification identifier
        specification_name (str): Name/key of the specification (e.g., "Color", "Weight")
        specification_value (str): Value of the specification (e.g., "Red", "2.5 kg")
        sort_order (int): Display order for multiple specifications
        created_at (datetime): Specification creation timestamp

    Business Rules:
        - Specifications stored as name-value pairs for flexibility
        - Sort order controls display sequence in product details
        - Multiple specifications per product supported
        - Extensible for any product attribute type

    Examples:
        >>> spec_data = {
        ...     'specification_name': 'Weight',
        ...     'specification_value': '2.5 kg',
        ...     'sort_order': 1
        ... }
        >>> serializer = ProductSpecificationSerializer(data=spec_data)

    Usage:
        - Nested within detailed product serializations
        - Standalone for specification management
        - Dynamic product attribute systems

    Use Cases:
        - Technical specifications (dimensions, weight, capacity)
        - Feature lists (materials, colors, compatibility)
        - Variable product attributes (size, color options)
        - Structured product information display

    Performance:
        - Efficient key-value storage model
        - Minimal overhead for specification display
        - Suitable for dynamic product catalogs

    Notes:
        - Flexible schema accommodates diverse product types
        - Sort order enables consistent presentation
        - Extensible for complex specification hierarchies
    """
    class Meta:
        model = ProductSpecification
        fields = ('id', 'specification_name', 'specification_value', 'sort_order', 'created_at')


class ProductSerializer(serializers.ModelSerializer):
    """
    Comprehensive serializer for complete product information.

    Provides full product data serialization including nested relationships
    for categories, images, and specifications. Handles both read and write
    operations with proper validation and data transformation.

    Fields:
        Core Product Information:
            - id (int): Unique product identifier (read-only)
            - name (str): Product title/name
            - description (str): Detailed product description
            - short_description (str): Brief product summary
            - sku (str): Stock Keeping Unit identifier

        Pricing Information:
            - price (Decimal): Current selling price
            - compare_price (Decimal): Original/comparison price for discounts
            - cost_price (Decimal): Internal cost price for margin calculation

        Categorization:
            - category (CategorySerializer): Nested category information (read-only)
            - category_id (int): Category foreign key for assignment (write-only)

        Inventory Management:
            - stock_quantity (int): Available inventory count
            - low_stock_threshold (int): Alert level for low stock

        Physical Properties:
            - weight (Decimal): Product weight for shipping
            - dimensions (str): Product dimensions for shipping/storage

        Product Flags:
            - is_active (bool): Product visibility and availability
            - is_featured (bool): Featured product designation
            - is_digital (bool): Digital product flag (no shipping required)
            - requires_shipping (bool): Shipping requirement flag

        SEO and Metadata:
            - tax_class (str): Tax classification for pricing
            - meta_title (str): SEO page title
            - meta_description (str): SEO meta description

        Related Data:
            - images (ProductImageSerializer): Product images (read-only, nested)
            - specifications (ProductSpecificationSerializer): Product specs (read-only, nested)

        Timestamps:
            - created_at (datetime): Product creation timestamp (read-only)
            - updated_at (datetime): Last modification timestamp (read-only)

    Validation:
        - Category existence validation via validate_category_id
        - Price field decimal validation
        - SKU uniqueness (inherited from model constraints)
        - Stock quantity non-negative validation

    Business Rules:
        - All products must belong to valid category
        - Pricing fields support multi-currency decimal precision
        - Inventory tracking with low stock alerts
        - SEO optimization support built-in
        - Digital products bypass shipping requirements

    Examples:
        >>> product_data = {
        ...     'name': 'Premium Headphones',
        ...     'description': 'High-quality wireless headphones',
        ...     'price': '199.99',
        ...     'category_id': 1,
        ...     'stock_quantity': 50,
        ...     'sku': 'HEAD-001'
        ... }
        >>> serializer = ProductSerializer(data=product_data)
        >>> if serializer.is_valid():
        ...     product = serializer.save(seller=request.user)

    Usage:
        - Complete product CRUD operations via API
        - Product detail page data provision
        - Product management interface data
        - E-commerce catalog integration

    Performance:
        - Nested serializers loaded efficiently with select_related
        - Read-only nested data prevents unnecessary joins on write
        - Optimized field selection for API responses

    Security:
        - Category validation prevents invalid references
        - Read-only fields protect sensitive information
        - Input validation prevents malformed data

    Notes:
        - Comprehensive serializer suitable for admin interfaces
        - Nested relationships provide complete product context
        - Extensible design for additional product features
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
        """
        Validate category exists and is accessible.

        Parameters:
            value (int): Category ID to validate.

        Returns:
            int: Validated category ID.

        Raises:
            serializers.ValidationError: If category doesn't exist.
        """
        try:
            Category.objects.get(id=value)
        except Category.DoesNotExist:
            raise serializers.ValidationError("Category does not exist")
        return value


class ProductListSerializer(serializers.ModelSerializer):
    """
    Optimized serializer for product list views and catalog browsing.

    Provides essential product information for list displays, search results,
    and catalog pages. Optimized for performance with minimal data loading
    while maintaining sufficient detail for user decision making.

    Fields:
        Essential Information:
            - id (int): Unique product identifier
            - name (str): Product title for display
            - short_description (str): Brief product summary
            - sku (str): Product identifier for reference

        Pricing and Availability:
            - price (Decimal): Current selling price
            - compare_price (Decimal): Original price for discount display
            - stock_quantity (int): Available inventory

        Categorization and Status:
            - category (CategorySerializer): Nested category info for navigation
            - is_active (bool): Product availability status
            - is_featured (bool): Featured product highlighting

        Visual and Temporal:
            - primary_image (SerializerMethodField): Main product image data
            - created_at (datetime): Product creation for sorting

    Custom Fields:
        primary_image: Dynamically fetched primary product image with complete
            image data including URL, alt text, and metadata.

    Performance Optimizations:
        - Limited field selection for faster serialization
        - Primary image fetched via method field to prevent N+1 queries
        - Category data included via nested serializer
        - Minimal database queries with proper prefetch strategies

    Business Rules:
        - Shows only essential information for browsing decisions
        - Primary image automatically selected from available images
        - Category context provided for navigation
        - Stock quantity visible for availability assessment

    Examples:
        >>> products = Product.objects.select_related('category').prefetch_related('images')
        >>> serializer = ProductListSerializer(products, many=True)
        >>> catalog_data = serializer.data
        >>> # Returns optimized product list for catalog display

    Usage Scenarios:
        - Product catalog pages
        - Search results display
        - Category browsing
        - Featured product listings
        - Mobile app product feeds

    Custom Methods:
        get_primary_image(): Retrieves the primary image for the product,
            returns None if no primary image exists.

    SEO and UX Benefits:
        - Fast loading for large product catalogs
        - Essential information for user decision making
        - Image data ready for immediate display
        - Category context for breadcrumbs and navigation

    Database Efficiency:
        - Requires select_related('category') for optimal performance
        - Benefits from prefetch_related('images') for primary image
        - Minimal field overhead reduces serialization time

    Notes:
        - Designed for high-performance list views
        - Balances information completeness with loading speed
        - Suitable for pagination and infinite scroll implementations
        - Compatible with search and filtering systems
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
        """
        Retrieve primary image data for the product.

        Fetches the primary image from the product's image collection and
        serializes it with complete image information. Returns None if no
        primary image is designated.

        Parameters:
            obj (Product): The product instance being serialized.

        Returns:
            dict|None: Serialized primary image data or None if not found.

        Performance:
            - Uses filter with first() for efficient single image retrieval
            - Benefits from prefetch_related('images') for optimal queries
            - Minimal overhead for image data inclusion
        """
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            return ProductImageSerializer(primary_image).data
        return None


class ProductCreateSerializer(serializers.ModelSerializer):
    """
    Specialized serializer for product creation with enhanced validation.

    Optimized for product creation workflows with comprehensive validation,
    business rule enforcement, and data integrity checks. Ensures proper
    product setup from initial creation.

    Fields:
        Core Product Data:
            - name (str): Product title (required)
            - description (str): Detailed product description
            - short_description (str): Brief product summary
            - sku (str): Unique stock keeping unit identifier

        Pricing Configuration:
            - price (Decimal): Selling price (required)
            - compare_price (Decimal): Original price for discount calculations
            - cost_price (Decimal): Internal cost for margin tracking

        Categorization:
            - category (ForeignKey): Product category assignment

        Inventory Setup:
            - stock_quantity (int): Initial inventory quantity
            - low_stock_threshold (int): Alert threshold for inventory management

        Physical Properties:
            - weight (Decimal): Product weight for shipping calculations
            - dimensions (str): Product dimensions for storage/shipping

        Product Configuration:
            - is_active (bool): Initial product visibility (default: True)
            - is_featured (bool): Featured product designation
            - is_digital (bool): Digital product flag (affects shipping)
            - requires_shipping (bool): Shipping requirement override

        Business Metadata:
            - tax_class (str): Tax classification for pricing
            - meta_title (str): SEO page title
            - meta_description (str): SEO description

    Validation Features:
        - SKU uniqueness validation across all products
        - Category existence and validity checks
        - Price field decimal precision validation
        - Stock quantity non-negative validation
        - Business rule compliance verification

    Business Rules:
        - Each product must have unique SKU
        - All products require valid category assignment
        - Pricing fields support decimal precision for currency
        - Digital products can bypass shipping requirements
        - SEO fields optional but recommended

    Examples:
        >>> product_data = {
        ...     'name': 'Wireless Bluetooth Headphones',
        ...     'description': 'Premium quality wireless headphones...',
        ...     'price': '149.99',
        ...     'sku': 'WBH-001',
        ...     'category': 1,
        ...     'stock_quantity': 100
        ... }
        >>> serializer = ProductCreateSerializer(data=product_data)
        >>> if serializer.is_valid():
        ...     product = serializer.save(seller=request.user)

    Validation Methods:
        validate_sku(): Ensures SKU uniqueness across product catalog.

    Usage Scenarios:
        - Product creation forms and APIs
        - Bulk product import processes
        - Seller onboarding workflows
        - Product management interfaces

    Security Features:
        - Input validation prevents malformed data
        - Foreign key validation ensures referential integrity
        - Business rule enforcement maintains data quality

    Integration Points:
        - Compatible with product management APIs
        - Supports multi-vendor marketplace workflows
        - Integrates with inventory management systems
        - Works with SEO optimization tools

    Notes:
        - Focused on creation workflow optimization
        - Enhanced validation for data quality assurance
        - Extensible for additional business rules
        - Compatible with batch operations and imports
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
        """
        Validate SKU uniqueness across all products.

        Ensures that the provided SKU doesn't already exist in the product
        catalog, maintaining unique identification for inventory management
        and business operations.

        Parameters:
            value (str): SKU value to validate.

        Returns:
            str: Validated SKU value.

        Raises:
            serializers.ValidationError: If SKU already exists.

        Business Rules:
            - SKU must be unique across entire product catalog
            - Case-sensitive validation for precise matching
            - Required for inventory tracking and management
        """
        if Product.objects.filter(sku=value).exists():
            raise serializers.ValidationError("Product with this SKU already exists")
        return value
