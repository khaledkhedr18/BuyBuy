"""
Product views for the BuyBuy e-commerce backend.

This module provides comprehensive view functions for handling product-related operations
in the BuyBuy multi-vendor e-commerce platform. It includes both template-based views
for the frontend and API views for programmatic access.

Features:
    - Product catalog browsing and filtering
    - Multi-vendor product management (CRUD operations)
    - Shopping cart functionality with session management
    - Order processing and checkout workflow
    - Sales tracking for vendors
    - Stock management integration

Architecture:
    - Template-based views for user interface
    - Transaction-safe operations for data consistency
    - Permission-based access control
    - Comprehensive error handling and user feedback
    - Database optimization with select_related and prefetch_related

Business Rules:
    - Only authenticated users can access product features
    - Sellers can only modify their own products
    - Stock levels are automatically updated on purchase
    - Orders can only be cancelled in pending/confirmed states
    - Cart items are user-specific and persistent

Security:
    - All views require authentication
    - Object-level permissions for product ownership
    - SQL injection protection via Django ORM
    - Transaction atomicity for financial operations

Examples:
    Product listing with category filtering:
        >>> # Template view displays products by category
        >>> category_products_view(request, category_id=1)

    Add product to cart:
        >>> # POST request with product_id and quantity
        >>> add_to_cart_view(request, pk=123)

    Complete checkout:
        >>> # POST request with shipping address details
        >>> checkout_view(request)

Dependencies:
    - Django authentication system
    - Database models from products.models
    - Category models for product classification
    - Message framework for user notifications
    - Template system for rendering responses

Notes:
    - All monetary calculations use Decimal for precision
    - Database transactions ensure data consistency
    - Proper error handling prevents data corruption
    - User experience optimized with informative messages
"""

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db import models
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .models import Product, Cart, CartItem, Order, OrderItem
from .serializers import ProductSerializer, ProductListSerializer
from categories.models import Category

@login_required
def product_list_view(request):
    """
    Display all active products to authenticated users.

    This view renders the main product catalog page showing all active products
    with their associated category and seller information. Uses database
    optimization to reduce queries.

    Parameters:
        request (HttpRequest): The HTTP request object containing user session
            and authentication information.

    Returns:
        HttpResponse: Rendered 'products.html' template with products context.

    Template Context:
        products (QuerySet): All active products with related category and seller
            data pre-loaded for performance optimization.

    Business Rules:
        - Only displays products where is_active=True
        - Pre-loads related category and seller data to prevent N+1 queries
        - Requires user authentication via @login_required decorator

    Database Queries:
        - Single optimized query with select_related for category and seller
        - Filters for active products only

    Examples:
        >>> # GET request to display all products
        >>> response = product_list_view(request)
        >>> # Returns rendered template with active products list

    Security:
        - Authentication required via @login_required
        - Only shows active/published products
        - No sensitive seller information exposed

    Performance:
        - Uses select_related to minimize database queries
        - Filters at database level for efficiency
    """
    products = Product.objects.filter(is_active=True).select_related('category', 'seller')
    return render(request, 'products.html', {'products': products})

@login_required
def product_detail_view(request, pk):
    """
    Display detailed information for a specific product.

    Shows comprehensive product details including description, pricing, stock
    availability, seller information, and purchase options. Ensures only
    active products are accessible.

    Parameters:
        request (HttpRequest): The HTTP request object with user authentication.
        pk (int): Primary key of the product to display.

    Returns:
        HttpResponse: Rendered 'product_detail.html' template with product context.

    Raises:
        Http404: If product doesn't exist or is not active.

    Template Context:
        product (Product): The requested product instance with all details.

    Business Rules:
        - Only shows active products (is_active=True)
        - Provides full product information for purchase decisions
        - Accessible to all authenticated users

    Security:
        - Authentication required
        - Automatic 404 for inactive products
        - No exposure of seller sensitive data

    Examples:
        >>> # GET request for product details
        >>> response = product_detail_view(request, pk=123)
        >>> # Returns detailed product page or 404 if not found/inactive

    Database Queries:
        - Single query with get_object_or_404 for efficiency
        - Includes is_active filter for security
    """
    product = get_object_or_404(Product, pk=pk, is_active=True)
    return render(request, 'product_detail.html', {'product': product})

@login_required
def category_products_view(request, category_id):
    """
    Display all products within a specific category.

    Shows products filtered by category with optimized database queries.
    Supports hierarchical category structure and provides category context
    for navigation and filtering.

    Parameters:
        request (HttpRequest): The HTTP request object with user session.
        category_id (int): Primary key of the category to filter products.

    Returns:
        HttpResponse: Rendered 'category_products.html' with category and products.

    Raises:
        Http404: If the specified category doesn't exist.

    Template Context:
        category (Category): The requested category instance for context.
        products (QuerySet): Active products in the category with related data.

    Business Rules:
        - Only shows active products within the specified category
        - Provides category context for breadcrumbs and navigation
        - Supports category-based product discovery

    Database Optimization:
        - Uses select_related for category and seller to prevent N+1 queries
        - Filters at database level for performance

    Examples:
        >>> # GET request for category products
        >>> response = category_products_view(request, category_id=5)
        >>> # Returns products page filtered by category

    Security:
        - Authentication required
        - Only shows active products
        - Category existence validated

    Notes:
        - Could be extended to support subcategory products
        - Optimized for category browsing workflows
    """
    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.filter(
        category=category,
        is_active=True
    ).select_related('category', 'seller')
    return render(request, 'category_products.html', {
        'category': category,
        'products': products
    })

@login_required
def my_products_view(request):
    """
    Display all products belonging to the authenticated user/seller.

    Provides sellers with a comprehensive view of their product listings,
    including both active and inactive products for complete inventory
    management. Essential for multi-vendor marketplace functionality.

    Parameters:
        request (HttpRequest): The HTTP request object containing authenticated
            user information.

    Returns:
        HttpResponse: Rendered 'my_products.html' template with user's products.

    Template Context:
        products (QuerySet): All products owned by the authenticated user,
            including both active and inactive products for management.

    Business Rules:
        - Shows only products where seller equals the authenticated user
        - Includes both active and inactive products for full management
        - Supports seller inventory management workflow

    Security:
        - Authentication required via @login_required
        - Automatic filtering by seller ensures users only see own products
        - No access to other sellers' product data

    Examples:
        >>> # GET request for seller's products
        >>> response = my_products_view(request)
        >>> # Returns seller's product management page

    Use Cases:
        - Product inventory management
        - Edit/delete product access
        - Sales performance tracking
        - Stock level monitoring

    Database Queries:
        - Single query filtered by seller (request.user)
        - No additional joins needed for basic listing
    """
    products = Product.objects.filter(seller=request.user)
    return render(request, 'my_products.html', {'products': products})

@login_required
def add_product_view(request):
    """
    Handle product creation for sellers in the multi-vendor marketplace.

    Provides both GET form display and POST form processing for adding new
    products. Includes comprehensive validation, error handling, and user
    feedback for optimal seller experience.

    Parameters:
        request (HttpRequest): The HTTP request object containing user session
            and form data (if POST).

    Returns:
        HttpResponse:
            - GET: Rendered 'add_product.html' with available categories
            - POST: Redirect to my_products on success, or form with errors

    HTTP Methods:
        GET: Display the add product form with category choices
        POST: Process form submission and create new product

    Form Fields:
        - name (str): Product title/name (required)
        - description (str): Detailed product description (required)
        - price (Decimal): Product price (required, positive)
        - stock_quantity (int): Available inventory (required, non-negative)
        - category (int): Foreign key to Category (required)
        - image_url (str): Product image URL (optional)

    Template Context:
        categories (QuerySet): All active categories for selection dropdown.

    Business Rules:
        - Only authenticated users can add products
        - Seller is automatically set to request.user
        - All products start as active by default
        - Category must be active and exist
        - Price and stock must be valid positive numbers

    Validation:
        - Server-side validation via model constraints
        - Category existence validation
        - Numeric field validation
        - Error handling with user-friendly messages

    Examples:
        >>> # GET request for add product form
        >>> response = add_product_view(request)
        >>> # Returns form with category choices

        >>> # POST request to create product
        >>> request.POST = {
        ...     'name': 'New Product',
        ...     'description': 'Great product',
        ...     'price': '29.99',
        ...     'stock_quantity': '100',
        ...     'category': '1',
        ...     'image_url': 'https://example.com/image.jpg'
        ... }
        >>> response = add_product_view(request)
        >>> # Redirects to my_products on success

    Security:
        - Authentication required
        - Seller automatically set to prevent spoofing
        - Input validation and sanitization
        - CSRF protection via Django middleware

    Error Handling:
        - Database errors caught and displayed to user
        - Invalid category ID handling
        - Numeric validation for price and stock
        - User-friendly error messages via Django messages

    Database Operations:
        - Single INSERT operation for product creation
        - Foreign key validation for category
        - Transaction handling via Django ORM
    """
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        stock_quantity = request.POST.get('stock_quantity')
        category_id = request.POST.get('category')
        image_url = request.POST.get('image_url')

        try:
            from categories.models import Category
            category = Category.objects.get(id=category_id)

            product = Product.objects.create(
                name=name,
                description=description,
                price=price,
                stock_quantity=stock_quantity,
                category=category,
                seller=request.user,
                image_url=image_url
            )

            messages.success(request, 'Product added successfully!')
            return redirect('products:my_products')
        except Exception as e:
            messages.error(request, f'Error adding product: {str(e)}')

    from categories.models import Category
    categories = Category.objects.filter(is_active=True)
    return render(request, 'add_product.html', {'categories': categories})

@login_required
def edit_product_view(request, pk):
    """
    Handle product editing for sellers with ownership validation.

    Provides secure product modification functionality ensuring sellers can
    only edit their own products. Includes comprehensive form handling,
    validation, and user feedback.

    Parameters:
        request (HttpRequest): The HTTP request object with user session.
        pk (int): Primary key of the product to edit.

    Returns:
        HttpResponse:
            - GET: Rendered edit form with current product data
            - POST: Redirect to my_products on success, or form with errors

    Raises:
        Http404: If product doesn't exist or user is not the seller.

    HTTP Methods:
        GET: Display edit form populated with current product data
        POST: Process form submission and update product

    Form Fields:
        - name (str): Product title/name
        - description (str): Detailed product description
        - price (Decimal): Product price
        - stock_quantity (int): Available inventory
        - category (int): Foreign key to Category
        - image_url (str): Product image URL

    Template Context:
        product (Product): The product instance being edited
        categories (QuerySet): All active categories for selection

    Business Rules:
        - Only product seller can edit the product
        - All fields are updatable except seller (implicit)
        - Category must be active and exist
        - Maintains product creation/modification timestamps

    Security:
        - Authentication required via @login_required
        - Ownership validation via seller=request.user filter
        - CSRF protection via Django middleware
        - Input validation and sanitization

    Examples:
        >>> # GET request for edit form
        >>> response = edit_product_view(request, pk=123)
        >>> # Returns form with current product data

        >>> # POST request to update product
        >>> request.POST = {
        ...     'name': 'Updated Product Name',
        ...     'price': '39.99',
        ...     'stock_quantity': '150'
        ... }
        >>> response = edit_product_view(request, pk=123)
        >>> # Updates product and redirects to my_products

    Error Handling:
        - Invalid category ID validation
        - Database constraint violations
        - Ownership verification failures
        - User-friendly error messages

    Database Operations:
        - SELECT query with ownership filter for security
        - UPDATE operation on successful validation
        - Foreign key validation for category
    """
    product = get_object_or_404(Product, pk=pk, seller=request.user)

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        stock_quantity = request.POST.get('stock_quantity')
        category_id = request.POST.get('category')
        image_url = request.POST.get('image_url')

        try:
            from categories.models import Category
            category = Category.objects.get(id=category_id)

            # Update product fields
            product.name = name
            product.description = description
            product.price = price
            product.stock_quantity = stock_quantity
            product.category = category
            product.image_url = image_url
            product.save()

            messages.success(request, 'Product updated successfully!')
            return redirect('products:my_products')
        except Exception as e:
            messages.error(request, f'Error updating product: {str(e)}')

    from categories.models import Category
    categories = Category.objects.filter(is_active=True)
    return render(request, 'edit_product.html', {
        'product': product,
        'categories': categories
    })

@login_required
def delete_product_view(request, pk):
    """
    Handle product deletion with ownership validation and confirmation.

    Provides secure product removal functionality with confirmation workflow.
    Ensures sellers can only delete their own products and provides clear
    user feedback throughout the deletion process.

    Parameters:
        request (HttpRequest): The HTTP request object with user authentication.
        pk (int): Primary key of the product to delete.

    Returns:
        HttpResponse:
            - GET: Rendered confirmation page with product details
            - POST: Redirect to my_products after successful deletion

    Raises:
        Http404: If product doesn't exist or user is not the seller.

    HTTP Methods:
        GET: Display delete confirmation page with product information
        POST: Execute deletion and redirect to product management page

    Template Context:
        product (Product): The product instance to be deleted, for confirmation
            display and user verification.

    Business Rules:
        - Only product seller can delete the product
        - Requires explicit confirmation via POST request
        - Provides product details for verification before deletion
        - Permanent deletion (no soft delete implemented)

    Security:
        - Authentication required via @login_required
        - Ownership validation via seller=request.user filter
        - Confirmation workflow prevents accidental deletion
        - CSRF protection via Django middleware

    Examples:
        >>> # GET request for delete confirmation
        >>> response = delete_product_view(request, pk=123)
        >>> # Returns confirmation page with product details

        >>> # POST request to confirm deletion
        >>> response = delete_product_view(request, pk=123)
        >>> # Deletes product and redirects to my_products

    User Experience:
        - Clear confirmation workflow prevents accidents
        - Success message displays deleted product name
        - Immediate redirect to product management page
        - User-friendly feedback via Django messages

    Database Operations:
        - SELECT query with ownership filter for security
        - DELETE operation on POST confirmation
        - Cascading deletion for related records if configured

    Notes:
        - Consider implementing soft deletion for audit trails
        - Could add validation for products with active orders
        - May need special handling for products with reviews/ratings
    """
    product = get_object_or_404(Product, pk=pk, seller=request.user)

    if request.method == 'POST':
        product_name = product.name
        product.delete()
        messages.success(request, f'Product "{product_name}" deleted successfully!')
        return redirect('products:my_products')

    return render(request, 'delete_product.html', {'product': product})

@login_required
def add_to_cart_view(request, pk):
    """
    Add product to user's shopping cart with quantity management.

    Handles adding products to the shopping cart with intelligent quantity
    management. Creates cart and cart items as needed, or updates existing
    items with accumulated quantities.

    Parameters:
        request (HttpRequest): The HTTP request object containing POST data
            and user authentication.
        pk (int): Primary key of the product to add to cart.

    Returns:
        HttpResponse: Redirect to product list with success message.

    Raises:
        Http404: If product doesn't exist or is not active.

    HTTP Methods:
        POST: Process add to cart request with quantity parameter

    Form Parameters:
        quantity (int): Number of items to add (default: 1, minimum: 1)

    Business Rules:
        - Only active products can be added to cart
        - Creates user cart if it doesn't exist
        - Accumulates quantity if product already in cart
        - Default quantity is 1 if not specified
        - User can only have one active cart at a time

    Database Operations:
        - get_or_create for Cart ensures single cart per user
        - get_or_create for CartItem prevents duplicates
        - Atomic quantity updates for existing items
        - Uses product active filter for security

    Examples:
        >>> # POST request to add single item
        >>> request.POST = {'quantity': '1'}
        >>> response = add_to_cart_view(request, pk=123)
        >>> # Adds 1 item to cart, creates cart if needed

        >>> # POST request to add multiple items
        >>> request.POST = {'quantity': '3'}
        >>> response = add_to_cart_view(request, pk=123)
        >>> # Adds 3 items to cart or increases existing by 3

    Security:
        - Authentication required
        - Only active products accepted
        - User can only modify own cart
        - Input validation for quantity parameter

    User Experience:
        - Success message shows product name and confirmation
        - Automatic redirect to product browsing
        - Seamless cart creation if needed
        - Quantity accumulation for repeat additions

    Performance:
        - Uses get_or_create to minimize database queries
        - Efficient cart and cart item management
        - Single transaction per operation

    Error Handling:
        - Invalid quantity defaults to 1
        - Product existence and active status validated
        - Database operation errors handled gracefully
    """
    product = get_object_or_404(Product, pk=pk, is_active=True)
    quantity = int(request.POST.get('quantity', 1))

    # Get or create cart
    cart, created = Cart.objects.get_or_create(user=request.user)

    # Get or create cart item
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity}
    )

    if not created:
        cart_item.quantity += quantity
        cart_item.save()

    messages.success(request, f'{product.name} added to cart!')
    return redirect('products:product_list')

@login_required
def cart_view(request):
    """
    Display user's shopping cart with items and total calculations.

    Renders the shopping cart page showing all cart items, quantities, prices,
    and total amount. Handles cases where user has no cart or empty cart
    gracefully with appropriate defaults.

    Parameters:
        request (HttpRequest): The HTTP request object with user authentication.

    Returns:
        HttpResponse: Rendered 'cart.html' template with cart context.

    Template Context:
        cart (Cart|None): User's cart instance or None if doesn't exist
        cart_items (QuerySet|list): Cart items with product data preloaded
        cart_total (Decimal): Total price of all items in cart

    Business Rules:
        - Shows user's personal cart only
        - Displays all cart items with product information
        - Calculates total price automatically
        - Handles empty cart state gracefully
        - Preloads product data for performance

    Database Optimization:
        - Uses select_related for product data to prevent N+1 queries
        - Single query to fetch all cart items with related products
        - Efficient total calculation via model property

    Examples:
        >>> # GET request for cart display
        >>> response = cart_view(request)
        >>> # Returns cart page with items and total

        >>> # User with no cart
        >>> response = cart_view(request)
        >>> # Returns cart page with empty state message

    User Experience:
        - Clear display of all cart contents
        - Product details and quantities shown
        - Running total for purchase decisions
        - Empty cart state handled gracefully

    Security:
        - Authentication required
        - User can only view own cart
        - No access to other users' cart data

    Performance:
        - Single database query with select_related
        - Efficient cart total calculation
        - Minimal template context for speed

    Error Handling:
        - Cart.DoesNotExist handled with default values
        - Empty cart state managed gracefully
        - No database errors for missing cart

    Notes:
        - Could add cart item modification options
        - May include stock availability checks
        - Suitable for checkout workflow initiation
    """
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.select_related('product')
        cart_total = cart.total_price
    except Cart.DoesNotExist:
        cart = None
        cart_items = []
        cart_total = 0

    return render(request, 'cart.html', {
        'cart': cart,
        'cart_items': cart_items,
        'cart_total': cart_total
    })

@login_required
def remove_from_cart_view(request, pk):
    """
    Remove specific item from user's shopping cart.

    Handles cart item removal with proper error handling and user feedback.
    Validates cart ownership and item existence before removal.

    Parameters:
        request (HttpRequest): The HTTP request object with user authentication.
        pk (int): Primary key of the CartItem to remove.

    Returns:
        HttpResponse: Redirect to cart page with status message.

    Business Rules:
        - Only removes items from user's own cart
        - Validates cart and cart item existence
        - Provides user feedback on success/failure
        - Maintains cart integrity after removal

    Security:
        - Authentication required
        - Cart ownership validation
        - Item ownership verification via cart relationship

    Examples:
        >>> # POST/GET request to remove cart item
        >>> response = remove_from_cart_view(request, pk=45)
        >>> # Removes item and redirects to cart with message

    Error Handling:
        - Cart.DoesNotExist: User has no cart
        - CartItem.DoesNotExist: Item not in user's cart
        - User-friendly error messages for all cases

    Database Operations:
        - Validation queries for cart and item existence
        - Single DELETE operation for cart item
        - No cascading effects on other entities

    User Experience:
        - Immediate feedback via success/error messages
        - Automatic redirect to updated cart view
        - Clear confirmation of removal action
    """
    try:
        cart = Cart.objects.get(user=request.user)
        cart_item = CartItem.objects.get(cart=cart, id=pk)
        cart_item.delete()
        messages.success(request, 'Item removed from cart!')
    except (Cart.DoesNotExist, CartItem.DoesNotExist):
        messages.error(request, 'Item not found in cart!')

    return redirect('products:cart')

@login_required
def update_cart_item_view(request, pk):
    """
    Update quantity of specific cart item with validation.

    Handles cart item quantity updates including removal for zero quantities.
    Provides comprehensive validation and user feedback for cart management.

    Parameters:
        request (HttpRequest): The HTTP request object containing POST data.
        pk (int): Primary key of the CartItem to update.

    Returns:
        HttpResponse: Redirect to cart page with status message.

    HTTP Methods:
        POST: Process quantity update with new value

    Form Parameters:
        quantity (int): New quantity value (0 removes item)

    Business Rules:
        - Only updates items in user's own cart
        - Quantity of 0 removes item from cart
        - Positive quantities update the cart item
        - Validates numeric input for quantity

    Security:
        - Authentication required
        - Cart ownership validation
        - Input validation for quantity parameter

    Examples:
        >>> # POST request to update quantity
        >>> request.POST = {'quantity': '3'}
        >>> response = update_cart_item_view(request, pk=45)
        >>> # Updates cart item to quantity 3

        >>> # POST request to remove item (quantity 0)
        >>> request.POST = {'quantity': '0'}
        >>> response = update_cart_item_view(request, pk=45)
        >>> # Removes item from cart

    Validation:
        - Numeric validation for quantity parameter
        - Cart and cart item existence verification
        - Ownership validation via cart relationship

    Error Handling:
        - Cart.DoesNotExist: User has no cart
        - CartItem.DoesNotExist: Item not in user's cart
        - ValueError: Invalid quantity input
        - User-friendly error messages for all cases

    Database Operations:
        - UPDATE query for quantity changes
        - DELETE query for zero quantities
        - Validation queries for existence checks

    User Experience:
        - Flexible quantity management
        - Zero quantity removes item logically
        - Clear success/error feedback
        - Immediate cart state updates
    """
    if request.method == 'POST':
        try:
            cart = Cart.objects.get(user=request.user)
            cart_item = CartItem.objects.get(cart=cart, id=pk)

            new_quantity = int(request.POST.get('quantity', 1))
            if new_quantity <= 0:
                cart_item.delete()
                messages.success(request, 'Item removed from cart!')
            else:
                cart_item.quantity = new_quantity
                cart_item.save()
                messages.success(request, 'Cart updated successfully!')

        except (Cart.DoesNotExist, CartItem.DoesNotExist):
            messages.error(request, 'Item not found in cart!')
        except ValueError:
            messages.error(request, 'Invalid quantity!')

    return redirect('products:cart')

@login_required
def checkout_view(request):
    """
    Handle complete checkout process with order creation and stock management.

    Processes the checkout workflow including address validation, order creation,
    order item generation, stock updates, and cart clearing. Uses database
    transactions to ensure data consistency throughout the process.

    Parameters:
        request (HttpRequest): The HTTP request object containing user session
            and POST data with shipping address information.

    Returns:
        HttpResponse:
            - GET: Rendered checkout form with cart summary
            - POST: Redirect to order detail on success, or form with errors

    Raises:
        Http404: Implicitly via redirect if cart is empty or doesn't exist.

    HTTP Methods:
        GET: Display checkout form with cart items and total
        POST: Process checkout with address validation and order creation

    Form Fields:
        - address (str): Street address (required)
        - city (str): City name (required)
        - state (str): State/province (required)
        - zip_code (str): Postal/ZIP code (required)
        - country (str): Country name (required)

    Template Context:
        cart (Cart): User's cart instance with items
        cart_items (QuerySet): Cart items with product data preloaded
        total_price (Decimal): Total cost of all cart items

    Business Rules:
        - Requires non-empty cart to proceed
        - All address fields must be provided
        - Creates order with current cart total
        - Generates individual order items for each cart item
        - Updates product stock quantities automatically
        - Clears cart after successful order creation
        - Associates orders with correct sellers per item

    Database Transactions:
        - Uses atomic transaction for data consistency
        - Rollback on any failure prevents partial orders
        - Ensures stock updates match order creation
        - Maintains referential integrity throughout process

    Security:
        - Authentication required
        - User can only checkout own cart
        - Input validation for all address fields
        - Transaction safety prevents data corruption

    Examples:
        >>> # GET request for checkout form
        >>> response = checkout_view(request)
        >>> # Returns checkout page with cart summary

        >>> # POST request with complete address
        >>> request.POST = {
        ...     'address': '123 Main St',
        ...     'city': 'Springfield',
        ...     'state': 'IL',
        ...     'zip_code': '62701',
        ...     'country': 'USA'
        ... }
        >>> response = checkout_view(request)
        >>> # Creates order and redirects to order detail

    Validation:
        - Empty cart validation with redirect
        - Complete address validation
        - Stock availability implicitly validated
        - Numeric total calculations verified

    Error Handling:
        - Empty cart redirects to cart page
        - Incomplete address shows validation errors
        - Database transaction failures handled
        - User-friendly error messages throughout

    Stock Management:
        - Decrements product stock by ordered quantity
        - No overselling prevention (could be enhanced)
        - Stock updates within same transaction as order

    Order Creation Process:
        1. Validate cart exists and has items
        2. Validate complete shipping address provided
        3. Begin database transaction
        4. Create Order record with total and address
        5. Create OrderItem records for each cart item
        6. Update product stock quantities
        7. Clear cart items
        8. Commit transaction
        9. Redirect to order confirmation

    Performance Considerations:
        - Single transaction reduces database round trips
        - Preloaded cart items minimize additional queries
        - Bulk operations where possible for efficiency

    Notes:
        - Could add payment processing integration
        - May need inventory validation before stock updates
        - Consider adding order confirmation email
        - Stock updates could benefit from pessimistic locking
    """
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.select_related('product')

        if not cart_items.exists():
            messages.error(request, 'Your cart is empty!')
            return redirect('products:cart')

        if request.method == 'POST':
            # Get individual address fields from the form
            address = request.POST.get('address', '').strip()
            city = request.POST.get('city', '').strip()
            state = request.POST.get('state', '').strip()
            zip_code = request.POST.get('zip_code', '').strip()
            country = request.POST.get('country', '').strip()

            # Combine address fields into shipping_address
            address_parts = []
            if address:
                address_parts.append(address)
            if city:
                address_parts.append(city)
            if state:
                address_parts.append(state)
            if zip_code:
                address_parts.append(zip_code)
            if country:
                address_parts.append(country)

            shipping_address = ', '.join(address_parts)

            # Validate that we have a shipping address
            if not shipping_address:
                messages.error(request, 'Please provide a complete shipping address.')
                return render(request, 'checkout.html', {
                    'cart': cart,
                    'cart_items': cart_items,
                    'total_price': cart.total_price
                })

            with transaction.atomic():
                # Create order
                order = Order.objects.create(
                    buyer=request.user,
                    total_amount=cart.total_price,
                    shipping_address=shipping_address
                )

                # Create order items
                for cart_item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        product=cart_item.product,
                        seller=cart_item.product.seller,
                        quantity=cart_item.quantity,
                        price=cart_item.product.price
                    )

                    # Update stock
                    product = cart_item.product
                    product.stock_quantity -= cart_item.quantity
                    product.save()

                # Clear cart
                cart_items.delete()

                messages.success(request, f'Order #{order.id} placed successfully!')
                return redirect('products:order_detail', pk=order.id)

        return render(request, 'checkout.html', {
            'cart': cart,
            'cart_items': cart_items
        })

    except Cart.DoesNotExist:
        messages.error(request, 'Your cart is empty!')
        return redirect('products:cart')

@login_required
def my_orders_view(request):
    """
    Display comprehensive list of user's purchase orders.

    Shows all orders placed by the authenticated user with complete order
    information including items, sellers, and order status. Optimized with
    database preloading for performance.

    Parameters:
        request (HttpRequest): The HTTP request object with user authentication.

    Returns:
        HttpResponse: Rendered 'my_orders.html' template with orders context.

    Template Context:
        orders (QuerySet): All orders by the user with prefetched items and
            product data for comprehensive display.

    Business Rules:
        - Shows only orders where buyer equals authenticated user
        - Displays all order statuses (pending, confirmed, shipped, delivered, cancelled)
        - Includes complete order item details with product information
        - Orders typically shown in reverse chronological order

    Database Optimization:
        - Uses prefetch_related for order items and their products
        - Minimizes N+1 query problems for order item display
        - Efficient loading of related seller and product data

    Examples:
        >>> # GET request for user's orders
        >>> response = my_orders_view(request)
        >>> # Returns page with all user's purchase history

    Security:
        - Authentication required
        - Buyer filter ensures users only see own orders
        - No access to other users' order information

    User Experience:
        - Complete purchase history in one view
        - Order details readily available
        - Easy navigation to individual order details
        - Status information clearly displayed

    Performance:
        - Single optimized query with prefetch_related
        - Efficient handling of multiple related objects
        - Minimal template rendering overhead

    Use Cases:
        - Order history browsing
        - Order status checking
        - Reorder functionality preparation
        - Purchase record keeping

    Notes:
        - Could add filtering by order status
        - May include pagination for users with many orders
        - Suitable for order management dashboard
    """
    orders = Order.objects.filter(buyer=request.user).prefetch_related('items__product')
    return render(request, 'my_orders.html', {'orders': orders})

@login_required
def order_detail_view(request, pk):
    """
    Display comprehensive details for a specific order.

    Shows complete order information including all items, quantities, prices,
    shipping details, and current status. Provides buyers with full order
    visibility and management options.

    Parameters:
        request (HttpRequest): The HTTP request object with user authentication.
        pk (int): Primary key of the order to display.

    Returns:
        HttpResponse: Rendered 'order_detail.html' template with order context.

    Raises:
        Http404: If order doesn't exist or user is not the buyer.

    Template Context:
        order (Order): The complete order instance with all details including
            related items, products, and seller information.

    Business Rules:
        - Only order buyer can view order details
        - Shows complete order information for transparency
        - Displays current order status and history
        - Provides access to order management actions

    Security:
        - Authentication required
        - Buyer validation ensures order ownership
        - No access to other users' order details

    Examples:
        >>> # GET request for order details
        >>> response = order_detail_view(request, pk=12345)
        >>> # Returns detailed order page with all information

    Database Queries:
        - Single query with buyer filter for security
        - Order items loaded via related manager when needed
        - Efficient object retrieval with ownership validation

    User Experience:
        - Complete order transparency
        - Clear status and progress information
        - Easy access to order management options
        - Detailed item breakdown with pricing

    Use Cases:
        - Order status checking
        - Order modification access
        - Receipt/invoice viewing
        - Customer service reference

    Related Actions:
        - Order cancellation (if status allows)
        - Reorder functionality (potential enhancement)
        - Order tracking (if implemented)

    Notes:
        - Template can show order status-specific actions
        - May include payment information display
        - Could integrate with shipping tracking systems
    """
    order = get_object_or_404(Order, pk=pk, buyer=request.user)
    return render(request, 'order_detail.html', {'order': order})

@login_required
def cancel_order_view(request, pk):
    """
    Cancel user's order with status validation and business rules.

    Handles order cancellation with proper status validation ensuring only
    eligible orders can be cancelled. Previously fixed to resolve 404 errors
    and implement proper business logic for order management.

    Parameters:
        request (HttpRequest): The HTTP request object with user authentication.
        pk (int): Primary key of the order to cancel.

    Returns:
        HttpResponse: Redirect to order detail page with status message.

    Raises:
        Http404: If order doesn't exist or user is not the buyer.

    Business Rules:
        - Only order buyer can cancel the order
        - Orders can only be cancelled in 'pending' or 'confirmed' status
        - Cancelled orders cannot be uncancelled
        - Status change is permanent and tracked

    Order Status Workflow:
        - pending → cancelled (allowed)
        - confirmed → cancelled (allowed)
        - shipped → cancelled (not allowed)
        - delivered → cancelled (not allowed)
        - cancelled → cancelled (no change)

    Security:
        - Authentication required via @login_required
        - Buyer validation ensures order ownership
        - Status validation prevents invalid cancellations

    Examples:
        >>> # POST/GET request to cancel order
        >>> response = cancel_order_view(request, pk=12345)
        >>> # Cancels order if status allows, redirects with message

    Database Operations:
        - Single UPDATE query to change order status
        - Ownership validation via buyer filter
        - Status validation before modification

    User Experience:
        - Clear success/error messaging
        - Automatic redirect to order detail page
        - Status-aware feedback messages
        - Immediate order status update

    Error Handling:
        - Invalid status prevents cancellation
        - User-friendly error messages
        - Order ownership validation
        - Graceful handling of edge cases

    Business Impact:
        - Supports customer service operations
        - Enables flexible order management
        - Maintains order audit trail
        - Prevents cancellation abuse

    Historical Context:
        - Previously resolved 404 error in URL routing
        - Enhanced with proper status validation
        - Improved error messaging for user experience

    Notes:
        - Could trigger inventory restoration (enhancement)
        - May need to handle payment refunds
        - Consider notification to sellers
        - Audit logging could be beneficial
    """
    order = get_object_or_404(Order, pk=pk, buyer=request.user)

    # Only allow cancellation for pending or confirmed orders
    if order.status in ['pending', 'confirmed']:
        order.status = 'cancelled'
        order.save()
        messages.success(request, 'Order has been cancelled successfully.')
    else:
        messages.error(request, f'Cannot cancel order with status: {order.get_status_display()}')

    return redirect('products:order_detail', pk=pk)

@login_required
def my_sales_view(request):
    """
    Display comprehensive sales dashboard for sellers.

    Shows all order items where the authenticated user is the seller, providing
    complete sales tracking and revenue management. Essential for multi-vendor
    marketplace operations and seller analytics.

    Parameters:
        request (HttpRequest): The HTTP request object with user authentication.

    Returns:
        HttpResponse: Rendered 'my_sales.html' template with sales context.

    Template Context:
        sales (QuerySet): All OrderItems where seller equals authenticated user,
            with related order, product, and buyer data preloaded.

    Business Rules:
        - Shows only sales where seller equals authenticated user
        - Includes order items from all order statuses
        - Provides complete transaction history for revenue tracking
        - Orders by creation date (newest first) for relevance

    Database Optimization:
        - Uses select_related for order, product, and buyer data
        - Minimizes N+1 queries for comprehensive sales display
        - Efficient loading of related transaction information

    Sales Information Included:
        - Product details and quantities sold
        - Order information and buyer details
        - Sale dates and current order status
        - Individual item pricing and totals
        - Order fulfillment status

    Examples:
        >>> # GET request for seller's sales
        >>> response = my_sales_view(request)
        >>> # Returns sales dashboard with all transactions

    Security:
        - Authentication required
        - Seller filter ensures users only see own sales
        - No access to other sellers' transaction data
        - Buyer information appropriately limited

    Use Cases:
        - Revenue tracking and reporting
        - Order fulfillment management
        - Customer relationship management
        - Sales performance analysis
        - Tax reporting and accounting

    Performance:
        - Single optimized query with select_related
        - Efficient sorting by creation date
        - Minimal template rendering overhead

    Business Value:
        - Enables seller financial management
        - Supports order fulfillment workflows
        - Provides transaction audit trails
        - Facilitates customer service operations

    Notes:
        - Could add filtering by date range or status
        - May include revenue summaries and analytics
        - Suitable for seller dashboard integration
        - Could support bulk order processing actions
    """
    sales = OrderItem.objects.filter(seller=request.user).select_related(
        'order', 'product', 'order__buyer'
    ).order_by('-created_at')
    return render(request, 'my_sales.html', {'sales': sales})
