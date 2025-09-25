"""
Category models for the BuyBuy e-commerce backend.

This module provides the Category model with hierarchical structure support,
SEO optimization, and comprehensive product organization capabilities.
"""

from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator


class CategoryManager(models.Manager):
    """
    Custom manager for Category model with optimized queries.

    Provides methods for commonly used category operations
    with performance optimizations and business logic.
    """

    def get_active_categories(self):
        """
        Get all active categories ordered by sort order and name.

        Returns:
            QuerySet: Active categories with optimized ordering
        """
        return self.filter(is_active=True).order_by('sort_order', 'name')

    def get_root_categories(self):
        """
        Get all root-level (parent=None) active categories.

        Returns:
            QuerySet: Root categories for building navigation menus
        """
        return self.filter(parent=None, is_active=True).order_by('sort_order', 'name')

    def get_category_tree(self):
        """
        Get categories with their children for tree display.

        Returns:
            QuerySet: Categories prefetched with children for efficient tree rendering
        """
        return self.filter(is_active=True).select_related('parent').prefetch_related('children')


class Category(models.Model):
    """
    Product category model with hierarchical structure and SEO optimization.

    This model supports multi-level category hierarchies for organizing products,
    includes SEO metadata, and provides methods for navigating the category tree.

    Attributes:
        name (str): Display name of the category (max 200 chars)
        description (str, optional): Detailed category description
        slug (str): URL-friendly unique identifier, auto-generated from name
        parent (Category, optional): Parent category for hierarchy support
        is_active (bool): Whether category is visible and usable (default: True)
        sort_order (int): Display order within same parent level (default: 0)
        meta_title (str, optional): SEO page title (max 200 chars)
        meta_description (str, optional): SEO meta description
        created_at (datetime): Timestamp of category creation
        updated_at (datetime): Timestamp of last modification

    Relations:
        children: Reverse relation to child categories
        products: Related products in this category

    Methods:
        product_count: Get count of active products in category
        get_children: Get active child categories
        get_ancestors: Get all parent categories up to root
        get_descendants: Get all descendant categories recursively
        full_path: Get full category path as string
        is_leaf: Check if category has no children
        can_be_deleted: Check if category can be safely deleted

    Examples:
        >>> electronics = Category.objects.create(name="Electronics")
        >>> phones = Category.objects.create(name="Phones", parent=electronics)
        >>> print(phones.full_path)  # "Electronics > Phones"
        >>> print(electronics.product_count)  # 25
        >>> print(phones.get_ancestors())  # [<Category: Electronics>]
    """

    name = models.CharField(
        max_length=200,
        help_text="Display name of the category"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Detailed description of the category"
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        help_text="URL-friendly identifier, auto-generated from name"
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children',
        help_text="Parent category for hierarchical organization"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this category is visible and usable"
    )
    sort_order = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(9999)],
        help_text="Display order within the same parent level (0-9999)"
    )
    meta_title = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="SEO page title for search engines"
    )
    meta_description = models.TextField(
        blank=True,
        null=True,
        help_text="SEO meta description for search engines"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when category was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when category was last modified"
    )

    objects = CategoryManager()

    class Meta:
        db_table = 'categories'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['sort_order', 'name']
        indexes = [
            models.Index(fields=['slug'], name='categories_slug_idx'),
            models.Index(fields=['parent'], name='categories_parent_idx'),
            models.Index(fields=['is_active'], name='categories_active_idx'),
            models.Index(fields=['sort_order'], name='categories_sort_idx'),
            models.Index(fields=['name'], name='categories_name_idx'),
            models.Index(fields=['parent', 'is_active'], name='categories_parent_act_idx'),
            models.Index(fields=['sort_order', 'name'], name='categories_sort_name_idx'),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(sort_order__gte=0),
                name='categories_sort_order_positive'
            ),
            models.UniqueConstraint(
                fields=['parent', 'sort_order'],
                name='unique_sort_per_parent',
                condition=models.Q(is_active=True)
            )
        ]

    def save(self, *args, **kwargs):
        """
        Override save to auto-generate slug and validate hierarchy.

        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments

        Raises:
            ValueError: If trying to set self as parent (circular reference)
        """
        # Auto-generate slug if not provided
        if not self.slug:
            self.slug = slugify(self.name)

        # Prevent circular references
        if self.parent == self:
            raise ValueError("Category cannot be its own parent")

        # Ensure unique slug
        if not self.pk:  # New instance
            counter = 1
            original_slug = self.slug
            while Category.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1

        super().save(*args, **kwargs)

    def __str__(self):
        """
        String representation showing full category path.

        Returns:
            str: Full category path (e.g., "Electronics > Phones > Smartphones")
        """
        return self.full_path

    def __repr__(self):
        """
        Developer-friendly representation.

        Returns:
            str: Object representation with key attributes
        """
        return f"<Category(id={self.pk}, name='{self.name}', slug='{self.slug}')>"

    @property
    def product_count(self):
        """
        Get the number of active products in this category.

        Returns:
            int: Count of active products directly assigned to this category

        Note:
            This does not include products in subcategories.
            Use get_total_product_count() for recursive counting.
        """
        return self.products.filter(is_active=True).count()

    @property
    def full_path(self):
        """
        Get the full category path from root to this category.

        Returns:
            str: Category path separated by ' > ' (e.g., "Electronics > Phones")
        """
        if self.parent:
            return f"{self.parent.full_path} > {self.name}"
        return self.name

    @property
    def is_leaf(self):
        """
        Check if this category has no children.

        Returns:
            bool: True if category has no child categories
        """
        return not self.children.filter(is_active=True).exists()

    @property
    def depth_level(self):
        """
        Get the depth level of this category in the hierarchy.

        Returns:
            int: Depth level (0 for root categories, 1 for first level, etc.)
        """
        level = 0
        current = self.parent
        while current:
            level += 1
            current = current.parent
        return level

    def get_children(self):
        """
        Get all active child categories ordered by sort_order and name.

        Returns:
            QuerySet: Active child categories with proper ordering

        Example:
            >>> electronics = Category.objects.get(name="Electronics")
            >>> children = electronics.get_children()
            >>> for child in children:
            ...     print(child.name)
        """
        return self.children.filter(is_active=True).order_by('sort_order', 'name')

    def get_ancestors(self):
        """
        Get all ancestor categories from immediate parent to root.

        Returns:
            list[Category]: List of ancestor categories ordered from closest to root

        Example:
            >>> smartphone = Category.objects.get(name="Smartphones")
            >>> ancestors = smartphone.get_ancestors()
            >>> print([cat.name for cat in ancestors])  # ["Phones", "Electronics"]
        """
        ancestors = []
        current = self.parent
        while current:
            ancestors.append(current)
            current = current.parent
        return ancestors

    def get_descendants(self):
        """
        Get all descendant categories recursively.

        Returns:
            list[Category]: List of all descendant categories (depth-first traversal)

        Example:
            >>> electronics = Category.objects.get(name="Electronics")
            >>> descendants = electronics.get_descendants()
            >>> print([cat.name for cat in descendants])
        """
        descendants = []
        for child in self.get_children():
            descendants.append(child)
            descendants.extend(child.get_descendants())
        return descendants

    def get_total_product_count(self):
        """
        Get total count of active products including all subcategories.

        Returns:
            int: Total product count including products in descendant categories
        """
        total = self.product_count
        for child in self.get_children():
            total += child.get_total_product_count()
        return total

    def can_be_deleted(self):
        """
        Check if category can be safely deleted.

        Returns:
            tuple[bool, str]: (can_delete, reason) - deletion status and reason

        Example:
            >>> category = Category.objects.get(id=1)
            >>> can_delete, reason = category.can_be_deleted()
            >>> if not can_delete:
            ...     print(f"Cannot delete: {reason}")
        """
        # Check for active products
        if self.products.filter(is_active=True).exists():
            return False, "Category has active products assigned"

        # Check for active children
        if self.children.filter(is_active=True).exists():
            return False, "Category has active subcategories"

        return True, "Category can be safely deleted"

    def move_to_parent(self, new_parent):
        """
        Move this category to a new parent, validating hierarchy rules.

        Args:
            new_parent (Category or None): New parent category or None for root

        Raises:
            ValueError: If move would create circular reference or invalid hierarchy

        Example:
            >>> phones = Category.objects.get(name="Phones")
            >>> electronics = Category.objects.get(name="Electronics")
            >>> phones.move_to_parent(electronics)
        """
        # Prevent circular references
        if new_parent and (new_parent == self or self in new_parent.get_ancestors()):
            raise ValueError("Cannot move category: would create circular reference")

        # Prevent excessive nesting (max 5 levels)
        if new_parent and new_parent.depth_level >= 4:
            raise ValueError("Cannot move category: maximum nesting depth exceeded")

        self.parent = new_parent
        self.save()
