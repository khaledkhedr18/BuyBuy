"""
Product models for the BuyBuy e-commerce backend.

This module provides comprehensive product management models including
products, images, specifications, shopping cart functionality, and order processing
with support for multi-vendor marketplace operations.
"""

from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from decimal import Decimal

User = get_user_model()


class ProductManager(models.Manager):
    """
    Custom manager for Product model with optimized queries and business logic.

    Provides methods for commonly used product operations with performance
    optimizations and filtering capabilities.
    """

    def get_active_products(self):
        """
        Get all active products with related data.

        Returns:
            QuerySet: Active products with optimized queries for category and seller
        """
        return self.filter(is_active=True).select_related('category', 'seller')

    def get_products_by_category(self, category):
        """
        Get active products in a specific category.

        Args:
            category (Category): Category instance to filter by

        Returns:
            QuerySet: Active products in the specified category
        """
        return self.get_active_products().filter(category=category)

    def get_products_by_seller(self, seller):
        """
        Get active products by a specific seller.

        Args:
            seller (User): Seller user instance

        Returns:
            QuerySet: Active products by the specified seller
        """
        return self.get_active_products().filter(seller=seller)

    def get_low_stock_products(self, threshold=10):
        """
        Get products with stock below threshold.

        Args:
            threshold (int): Stock quantity threshold (default: 10)

        Returns:
            QuerySet: Products with low stock levels
        """
        return self.get_active_products().filter(stock_quantity__lte=threshold)


class Product(models.Model):
    """
    Product model for e-commerce marketplace items.

    This model represents individual products in the marketplace with support
    for multi-vendor selling, inventory management, and comprehensive product information.

    Attributes:
        name (str): Product display name (max 200 chars)
        description (str): Detailed product description
        short_description (str): Brief product summary (max 500 chars, optional)
        price (Decimal): Product price with 2 decimal precision
        stock_quantity (int): Available inventory quantity (non-negative)
        category (Category): Product category for organization
        seller (User): Vendor/seller who owns this product
        image_url (str): Primary product image URL (optional)
        is_active (bool): Whether product is visible and purchasable (default: True)
        created_at (datetime): Product creation timestamp
        updated_at (datetime): Last modification timestamp

    Relations:
        images: Multiple product images (ProductImage)
        specifications: Product attributes/specifications (ProductSpecification)
        cart_items: Cart items containing this product
        order_items: Order items for this product

    Methods:
        is_in_stock: Check if product has available stock
        can_purchase: Check if product can be purchased with quantity
        get_primary_image: Get primary product image
        update_stock: Update stock quantity with validation
        get_average_rating: Get average rating from reviews (if implemented)
        is_low_stock: Check if stock is below threshold

    Examples:
        >>> product = Product.objects.create(
        ...     name="iPhone 14",
        ...     price=Decimal('999.99'),
        ...     stock_quantity=50,
        ...     category=electronics_category,
        ...     seller=vendor_user
        ... )
        >>> print(product.is_in_stock())  # True
        >>> print(product.can_purchase(5))  # (True, "")
    """

    name = models.CharField(
        max_length=200,
        help_text="Product display name"
    )
    description = models.TextField(
        help_text="Detailed product description"
    )
    short_description = models.CharField(
        max_length=500,
        blank=True,
        help_text="Brief product summary for listings"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Product price (minimum $0.01)"
    )
    stock_quantity = models.PositiveIntegerField(
        default=0,
        help_text="Available inventory quantity"
    )
    category = models.ForeignKey(
        'categories.Category',
        on_delete=models.CASCADE,
        related_name='products',
        help_text="Product category for organization"
    )
    seller = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='products_selling',
        help_text="Vendor/seller who owns this product"
    )
    image_url = models.URLField(
        blank=True,
        null=True,
        help_text="Primary product image URL"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether product is visible and purchasable"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Product creation timestamp"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last modification timestamp"
    )

    objects = ProductManager()

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_active', 'category'], name='products_active_cat_idx'),
            models.Index(fields=['seller', 'is_active'], name='products_seller_act_idx'),
            models.Index(fields=['price'], name='products_price_idx'),
            models.Index(fields=['stock_quantity'], name='products_stock_idx'),
            models.Index(fields=['created_at'], name='products_created_idx'),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(price__gt=0),
                name='products_price_positive'
            ),
            models.CheckConstraint(
                check=models.Q(stock_quantity__gte=0),
                name='products_stock_non_negative'
            )
        ]

    def clean(self):
        """
        Validate product data before saving.

        Raises:
            ValidationError: If validation fails
        """
        if self.price <= 0:
            raise ValidationError('Product price must be positive.')

        if self.stock_quantity < 0:
            raise ValidationError('Stock quantity cannot be negative.')

        if not self.category.is_active:
            raise ValidationError('Product category must be active.')

    def save(self, *args, **kwargs):
        """
        Override save to perform validation and cleanup.

        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments
        """
        self.clean()

        # Generate short description if not provided
        if not self.short_description and self.description:
            self.short_description = (
                self.description[:497] + '...'
                if len(self.description) > 500
                else self.description
            )

        super().save(*args, **kwargs)

    def __str__(self):
        """
        String representation of the product.

        Returns:
            str: Product name with seller information
        """
        return f"{self.name} by {self.seller.get_full_name() or self.seller.username}"

    def __repr__(self):
        """
        Developer-friendly representation.

        Returns:
            str: Object representation with key attributes
        """
        return (
            f"<Product(id={self.pk}, name='{self.name}', "
            f"price={self.price}, stock={self.stock_quantity})>"
        )

    @property
    def is_in_stock(self):
        """
        Check if product has available stock.

        Returns:
            bool: True if stock quantity > 0 and product is active
        """
        return self.is_active and self.stock_quantity > 0

    @property
    def is_low_stock(self, threshold=10):
        """
        Check if product stock is below threshold.

        Args:
            threshold (int): Stock threshold (default: 10)

        Returns:
            bool: True if stock is below threshold
        """
        return self.stock_quantity <= threshold

    @property
    def display_price(self):
        """
        Get formatted price for display.

        Returns:
            str: Formatted price string (e.g., "$999.99")
        """
        return f"${self.price:,.2f}"

    def can_purchase(self, quantity=1):
        """
        Check if product can be purchased with specified quantity.

        Args:
            quantity (int): Desired purchase quantity

        Returns:
            tuple[bool, str]: (can_purchase, reason) - purchase status and reason

        Example:
            >>> product = Product.objects.get(id=1)
            >>> can_buy, reason = product.can_purchase(5)
            >>> if not can_buy:
            ...     print(f"Cannot purchase: {reason}")
        """
        if not self.is_active:
            return False, "Product is not available"

        if quantity <= 0:
            return False, "Quantity must be positive"

        if self.stock_quantity < quantity:
            return False, f"Insufficient stock (available: {self.stock_quantity})"

        return True, ""

    def get_primary_image(self):
        """
        Get the primary product image or first available image.

        Returns:
            ProductImage or None: Primary image instance or None if no images
        """
        # Try to get primary image first
        primary = self.images.filter(is_primary=True).first()
        if primary:
            return primary

        # Fall back to first image
        return self.images.first()

    def update_stock(self, quantity_change):
        """
        Update stock quantity with validation.

        Args:
            quantity_change (int): Change in stock (positive to add, negative to reduce)

        Raises:
            ValidationError: If resulting stock would be negative

        Example:
            >>> product.update_stock(-5)  # Reduce stock by 5
            >>> product.update_stock(10)  # Add 10 to stock
        """
        new_quantity = self.stock_quantity + quantity_change

        if new_quantity < 0:
            raise ValidationError(
                f"Cannot reduce stock by {abs(quantity_change)}. "
                f"Current stock: {self.stock_quantity}"
            )

        self.stock_quantity = new_quantity
        self.save(update_fields=['stock_quantity', 'updated_at'])

    def reserve_stock(self, quantity):
        """
        Reserve stock for order processing.

        Args:
            quantity (int): Quantity to reserve

        Returns:
            bool: True if successfully reserved

        Example:
            >>> if product.reserve_stock(3):
            ...     # Process order
            ...     pass
        """
        can_purchase, reason = self.can_purchase(quantity)
        if not can_purchase:
            return False

        try:
            self.update_stock(-quantity)
            return True
        except ValidationError:
            return False


class ProductImage(models.Model):
    """
    Product image model for multiple images per product.

    This model manages product images with support for primary image designation,
    alt text for accessibility, and ordering capabilities.

    Attributes:
        product (Product): Related product instance
        image_url (str): Image URL or file path
        alt_text (str): Alternative text for accessibility (optional)
        is_primary (bool): Whether this is the primary product image
        sort_order (int): Display order for image galleries
        created_at (datetime): Image upload timestamp

    Methods:
        set_as_primary: Set this image as the primary product image

    Examples:
        >>> ProductImage.objects.create(
        ...     product=product,
        ...     image_url="https://example.com/image1.jpg",
        ...     alt_text="iPhone 14 front view",
        ...     is_primary=True
        ... )
    """

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',
        help_text="Related product instance"
    )
    image_url = models.URLField(
        help_text="Image URL or file path"
    )
    alt_text = models.CharField(
        max_length=255,
        blank=True,
        help_text="Alternative text for accessibility"
    )
    is_primary = models.BooleanField(
        default=False,
        help_text="Whether this is the primary product image"
    )
    sort_order = models.PositiveIntegerField(
        default=0,
        help_text="Display order for image galleries"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Image upload timestamp"
    )

    class Meta:
        ordering = ['sort_order', 'created_at']
        indexes = [
            models.Index(fields=['product', 'is_primary'], name='prod_img_prod_primary_idx'),
            models.Index(fields=['product', 'sort_order'], name='prod_img_prod_sort_idx'),
        ]

    def __str__(self):
        """
        String representation of the product image.

        Returns:
            str: Image description with product name
        """
        primary_indicator = " (Primary)" if self.is_primary else ""
        return f"Image for {self.product.name}{primary_indicator}"

    def set_as_primary(self):
        """
        Set this image as the primary product image.

        This method ensures only one primary image per product by updating
        all other images of the same product to not be primary.
        """
        # Remove primary status from other images
        ProductImage.objects.filter(product=self.product, is_primary=True).update(is_primary=False)

        # Set this image as primary
        self.is_primary = True
        self.save(update_fields=['is_primary'])


class ProductSpecification(models.Model):
    """
    Product specifications and attributes model.

    This model stores key-value pairs for product specifications,
    attributes, and technical details.

    Attributes:
        product (Product): Related product instance
        name (str): Specification name (e.g., "Color", "Size", "Weight")
        value (str): Specification value (e.g., "Red", "Large", "1.5kg")
        created_at (datetime): Specification creation timestamp

    Examples:
        >>> ProductSpecification.objects.create(
        ...     product=product,
        ...     name="Screen Size",
        ...     value="6.1 inches"
        ... )
    """

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='specifications',
        help_text="Related product instance"
    )
    name = models.CharField(
        max_length=100,
        help_text="Specification name (e.g., 'Color', 'Size')"
    )
    value = models.CharField(
        max_length=255,
        help_text="Specification value (e.g., 'Red', 'Large')"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Specification creation timestamp"
    )

    class Meta:
        unique_together = ['product', 'name']
        ordering = ['name']
        indexes = [
            models.Index(fields=['product', 'name'], name='prod_specs_prod_name_idx'),
        ]

    def __str__(self):
        """
        String representation of the specification.

        Returns:
            str: Specification name and value
        """
        return f"{self.name}: {self.value}"


class CartManager(models.Manager):
    """
    Custom manager for Cart model with utility methods.
    """

    def get_or_create_for_user(self, user):
        """
        Get or create cart for a specific user.

        Args:
            user (User): User instance

        Returns:
            Cart: User's cart instance
        """
        cart, created = self.get_or_create(user=user)
        return cart


class Cart(models.Model):
    """
    Shopping cart model for user purchase sessions.

    This model manages user shopping carts with automatic totals calculation
    and cart item management functionality.

    Attributes:
        user (User): Cart owner (one-to-one relationship)
        created_at (datetime): Cart creation timestamp
        updated_at (datetime): Last modification timestamp

    Properties:
        total_price: Sum of all cart items' total prices
        total_items: Total quantity of items in cart
        is_empty: Whether cart has no items

    Methods:
        add_product: Add product to cart with quantity
        remove_product: Remove product from cart
        update_quantity: Update item quantity in cart
        clear: Remove all items from cart

    Examples:
        >>> cart = Cart.objects.get_or_create_for_user(user)
        >>> cart.add_product(product, quantity=2)
        >>> print(cart.total_price)  # Decimal('1999.98')
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='cart',
        help_text="Cart owner (one cart per user)"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Cart creation timestamp"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last modification timestamp"
    )

    objects = CartManager()

    class Meta:
        indexes = [
            models.Index(fields=['user'], name='carts_user_idx'),
        ]

    def __str__(self):
        """
        String representation of the cart.

        Returns:
            str: Cart description with user information
        """
        return f"Cart for {self.user.get_full_name() or self.user.username}"

    @property
    def total_price(self):
        """
        Calculate total price of all items in cart.

        Returns:
            Decimal: Total price of cart items
        """
        return sum(item.total_price for item in self.items.all()) or Decimal('0.00')

    @property
    def total_items(self):
        """
        Calculate total quantity of items in cart.

        Returns:
            int: Total quantity of all cart items
        """
        return sum(item.quantity for item in self.items.all()) or 0

    @property
    def is_empty(self):
        """
        Check if cart is empty.

        Returns:
            bool: True if cart has no items
        """
        return not self.items.exists()

    def add_product(self, product, quantity=1):
        """
        Add product to cart or update quantity if already exists.

        Args:
            product (Product): Product to add
            quantity (int): Quantity to add (default: 1)

        Returns:
            tuple[CartItem, bool]: (cart_item, created) - item and whether it was created

        Raises:
            ValidationError: If product cannot be purchased
        """
        can_purchase, reason = product.can_purchase(quantity)
        if not can_purchase:
            raise ValidationError(reason)

        cart_item, created = CartItem.objects.get_or_create(
            cart=self,
            product=product,
            defaults={'quantity': quantity}
        )

        if not created:
            # Update existing item quantity
            new_quantity = cart_item.quantity + quantity
            can_purchase, reason = product.can_purchase(new_quantity)
            if not can_purchase:
                raise ValidationError(reason)
            cart_item.quantity = new_quantity
            cart_item.save(update_fields=['quantity', 'updated_at'])

        return cart_item, created

    def remove_product(self, product):
        """
        Remove product from cart completely.

        Args:
            product (Product): Product to remove

        Returns:
            bool: True if product was removed, False if not in cart
        """
        try:
            cart_item = CartItem.objects.get(cart=self, product=product)
            cart_item.delete()
            return True
        except CartItem.DoesNotExist:
            return False

    def update_quantity(self, product, quantity):
        """
        Update quantity of product in cart.

        Args:
            product (Product): Product to update
            quantity (int): New quantity (0 removes item)

        Returns:
            CartItem or None: Updated cart item or None if removed

        Raises:
            ValidationError: If quantity is invalid or product unavailable
        """
        if quantity == 0:
            self.remove_product(product)
            return None

        if quantity < 0:
            raise ValidationError("Quantity must be non-negative")

        can_purchase, reason = product.can_purchase(quantity)
        if not can_purchase:
            raise ValidationError(reason)

        cart_item, created = CartItem.objects.get_or_create(
            cart=self,
            product=product,
            defaults={'quantity': quantity}
        )

        if not created:
            cart_item.quantity = quantity
            cart_item.save(update_fields=['quantity', 'updated_at'])

        return cart_item

    def clear(self):
        """
        Remove all items from cart.

        Returns:
            int: Number of items removed
        """
        count = self.items.count()
        self.items.all().delete()
        return count


class CartItem(models.Model):
    """
    Cart item model representing products in a user's shopping cart.

    This model manages individual items within shopping carts with
    quantity tracking and total price calculations.

    Attributes:
        cart (Cart): Related shopping cart
        product (Product): Product in the cart
        quantity (int): Quantity of the product (positive integer)
        created_at (datetime): Item addition timestamp
        updated_at (datetime): Last modification timestamp

    Properties:
        total_price: Product price × quantity
        unit_price: Product price at time of cart addition

    Examples:
        >>> cart_item = CartItem.objects.create(
        ...     cart=user_cart,
        ...     product=product,
        ...     quantity=2
        ... )
        >>> print(cart_item.total_price)  # Decimal('1999.98')
    """

    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        help_text="Related shopping cart"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        help_text="Product in the cart"
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Quantity of the product (minimum 1)"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Item addition timestamp"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last modification timestamp"
    )

    class Meta:
        unique_together = ['cart', 'product']
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['cart', 'product'], name='cart_items_cart_prod_idx'),
        ]

    def clean(self):
        """
        Validate cart item before saving.

        Raises:
            ValidationError: If validation fails
        """
        if self.quantity <= 0:
            raise ValidationError('Quantity must be positive.')

        can_purchase, reason = self.product.can_purchase(self.quantity)
        if not can_purchase:
            raise ValidationError(reason)

    def save(self, *args, **kwargs):
        """
        Override save to perform validation.

        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments
        """
        self.clean()
        super().save(*args, **kwargs)

    @property
    def total_price(self):
        """
        Calculate total price for this cart item.

        Returns:
            Decimal: Product price × quantity
        """
        return self.product.price * self.quantity

    @property
    def unit_price(self):
        """
        Get unit price of the product.

        Returns:
            Decimal: Product price per unit
        """
        return self.product.price

    def __str__(self):
        """
        String representation of the cart item.

        Returns:
            str: Quantity and product name
        """
        return f"{self.quantity} × {self.product.name}"


class OrderManager(models.Manager):
    """
    Custom manager for Order model with business logic methods.
    """

    def get_user_orders(self, user):
        """
        Get all orders for a specific user.

        Args:
            user (User): User instance

        Returns:
            QuerySet: User's orders with related data
        """
        return self.filter(buyer=user).select_related('buyer').prefetch_related('items')

    def get_pending_orders(self):
        """
        Get all pending orders that need processing.

        Returns:
            QuerySet: Orders with pending status
        """
        return self.filter(status='pending').select_related('buyer')


class Order(models.Model):
    """
    Order model for completed purchases with multi-vendor support.

    This model represents completed purchase orders with status tracking,
    shipping information, and support for order cancellation business rules.

    Attributes:
        buyer (User): Customer who placed the order
        total_amount (Decimal): Total order amount with 2 decimal precision
        status (str): Order status from predefined choices
        shipping_address (str): Delivery address for the order
        created_at (datetime): Order placement timestamp
        updated_at (datetime): Last status change timestamp

    Status Choices:
        - pending: Order placed but not confirmed
        - confirmed: Order confirmed and being prepared
        - shipped: Order shipped to customer
        - delivered: Order successfully delivered
        - cancelled: Order cancelled (can only cancel pending/confirmed orders)

    Relations:
        items: Order items containing products and pricing (OrderItem)

    Methods:
        can_be_cancelled: Check if order can be cancelled based on status
        cancel_order: Cancel the order and restore product stock
        get_seller_summary: Get summary of items grouped by seller
        calculate_total: Recalculate total from order items

    Examples:
        >>> order = Order.objects.create(
        ...     buyer=user,
        ...     total_amount=Decimal('1999.98'),
        ...     shipping_address="123 Main St, City, State",
        ...     status='pending'
        ... )
        >>> can_cancel, reason = order.can_be_cancelled()
        >>> if can_cancel:
        ...     order.cancel_order()
    """

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    buyer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders_bought',
        help_text="Customer who placed the order"
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Total order amount (minimum $0.01)"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Current order status"
    )
    shipping_address = models.TextField(
        help_text="Delivery address for the order"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Order placement timestamp"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last status change timestamp"
    )

    objects = OrderManager()

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['buyer', 'status'], name='orders_buyer_status_idx'),
            models.Index(fields=['status', 'created_at'], name='orders_status_created_idx'),
            models.Index(fields=['created_at'], name='orders_created_idx'),
        ]

    def clean(self):
        """
        Validate order data before saving.

        Raises:
            ValidationError: If validation fails
        """
        if self.total_amount <= 0:
            raise ValidationError('Order total must be positive.')

        if not self.shipping_address.strip():
            raise ValidationError('Shipping address is required.')

    def save(self, *args, **kwargs):
        """
        Override save to perform validation.

        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments
        """
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        """
        String representation of the order.

        Returns:
            str: Order number and buyer information
        """
        buyer_name = self.buyer.get_full_name() or self.buyer.username
        return f"Order #{self.id} by {buyer_name} ({self.get_status_display()})"

    def can_be_cancelled(self):
        """
        Check if order can be cancelled based on current status.

        Orders can only be cancelled if they are in 'pending' or 'confirmed' status.
        Once shipped or delivered, cancellation is not allowed.

        Returns:
            tuple[bool, str]: (can_cancel, reason) - cancellation status and reason

        Examples:
            >>> order = Order.objects.get(id=1)
            >>> can_cancel, reason = order.can_be_cancelled()
            >>> if can_cancel:
            ...     order.cancel_order()
            >>> else:
            ...     print(f"Cannot cancel: {reason}")
        """
        if self.status == 'cancelled':
            return False, "Order is already cancelled"

        if self.status in ['shipped', 'delivered']:
            return False, f"Cannot cancel {self.get_status_display().lower()} order"

        if self.status in ['pending', 'confirmed']:
            return True, "Order can be cancelled"

        return False, f"Cannot cancel order with status: {self.get_status_display()}"

    def cancel_order(self, restore_stock=True):
        """
        Cancel the order and optionally restore product stock.

        This method changes the order status to 'cancelled' and can restore
        stock quantities for all products in the order.

        Args:
            restore_stock (bool): Whether to restore product stock (default: True)

        Returns:
            bool: True if order was successfully cancelled

        Raises:
            ValidationError: If order cannot be cancelled

        Example:
            >>> order = Order.objects.get(id=1)
            >>> if order.cancel_order():
            ...     print("Order cancelled successfully")
        """
        can_cancel, reason = self.can_be_cancelled()
        if not can_cancel:
            raise ValidationError(reason)

        # Restore stock if requested
        if restore_stock:
            for item in self.items.all():
                try:
                    item.product.update_stock(item.quantity)
                except ValidationError:
                    # Log error but don't fail the cancellation
                    pass

        self.status = 'cancelled'
        self.save(update_fields=['status', 'updated_at'])
        return True

    def get_seller_summary(self):
        """
        Get summary of order items grouped by seller.

        Returns:
            dict: Dictionary with seller IDs as keys and item lists as values

        Example:
            >>> order = Order.objects.get(id=1)
            >>> summary = order.get_seller_summary()
            >>> for seller_id, items in summary.items():
            ...     print(f"Seller {seller_id}: {len(items)} items")
        """
        summary = {}
        for item in self.items.select_related('seller').all():
            seller_id = item.seller.id
            if seller_id not in summary:
                summary[seller_id] = {
                    'seller': item.seller,
                    'items': [],
                    'total_amount': Decimal('0.00')
                }
            summary[seller_id]['items'].append(item)
            summary[seller_id]['total_amount'] += item.total_price
        return summary

    def calculate_total(self):
        """
        Recalculate total amount from order items.

        Returns:
            Decimal: Calculated total amount from order items
        """
        return sum(item.total_price for item in self.items.all()) or Decimal('0.00')


class OrderItem(models.Model):
    """
    Order item model for products within completed orders.

    This model stores individual products within orders with pricing
    information captured at the time of purchase to maintain historical accuracy.

    Attributes:
        order (Order): Related order instance
        product (Product): Product that was ordered
        seller (User): Seller of the product (for multi-vendor support)
        quantity (int): Quantity ordered (positive integer)
        price (Decimal): Price per unit at time of purchase
        created_at (datetime): Order item creation timestamp

    Properties:
        total_price: Price × quantity for this item

    Examples:
        >>> order_item = OrderItem.objects.create(
        ...     order=order,
        ...     product=product,
        ...     seller=product.seller,
        ...     quantity=2,
        ...     price=product.price
        ... )
        >>> print(order_item.total_price)  # Price × quantity
    """

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        help_text="Related order instance"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        help_text="Product that was ordered"
    )
    seller = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders_sold',
        help_text="Seller of the product"
    )
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Quantity ordered (minimum 1)"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Price per unit at time of purchase"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Order item creation timestamp"
    )

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['order'], name='order_items_order_idx'),
            models.Index(fields=['seller', 'created_at'], name='order_items_seller_idx'),
            models.Index(fields=['product'], name='order_items_product_idx'),
        ]

    def clean(self):
        """
        Validate order item data.

        Raises:
            ValidationError: If validation fails
        """
        if self.quantity <= 0:
            raise ValidationError('Quantity must be positive.')

        if self.price <= 0:
            raise ValidationError('Price must be positive.')

    def save(self, *args, **kwargs):
        """
        Override save to perform validation and set seller.

        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments
        """
        # Auto-set seller from product if not provided
        if not self.seller_id:
            self.seller = self.product.seller

        self.clean()
        super().save(*args, **kwargs)

    @property
    def total_price(self):
        """
        Calculate total price for this order item.

        Returns:
            Decimal: Price × quantity
        """
        return self.price * self.quantity

    def __str__(self):
        """
        String representation of the order item.

        Returns:
            str: Quantity, product name, and order number
        """
        return f"{self.quantity} × {self.product.name} in Order #{self.order.id}"
