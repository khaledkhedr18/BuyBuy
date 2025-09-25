"""
Authentication models for the BuyBuy e-commerce backend.

This module provides custom user models with extended functionality for
the e-commerce platform, including profile information and JWT token management.
"""

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    """
    Custom user manager for creating users and superusers.

    This manager handles the creation of User instances with proper validation
    and normalization of email addresses.
    """

    def create_user(self, email, username, first_name, last_name, password=None, **extra_fields):
        """
        Create and save a regular user with the given email and password.

        Args:
            email (str): User's email address (must be unique)
            username (str): User's username
            first_name (str): User's first name
            last_name (str): User's last name
            password (str, optional): User's password
            **extra_fields: Additional fields for the user model

        Returns:
            User: The created user instance

        Raises:
            ValueError: If email or username is not provided
        """
        if not email:
            raise ValueError("Email address is required for user creation")
        if not username:
            raise ValueError("Username is required for user creation")

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, first_name, last_name, password=None, **extra_fields):
        """
        Create and save a superuser with the given email and password.

        Args:
            email (str): Superuser's email address
            username (str): Superuser's username
            first_name (str): Superuser's first name
            last_name (str): Superuser's last name
            password (str, optional): Superuser's password
            **extra_fields: Additional fields for the superuser

        Returns:
            User: The created superuser instance
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, username, first_name, last_name, password, **extra_fields)


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser for e-commerce functionality.

    This model represents a user in the BuyBuy e-commerce platform with email-based
    authentication and additional fields for user management.

    Attributes:
        email (EmailField): User's unique email address (used for authentication)
        first_name (CharField): User's first name (required)
        last_name (CharField): User's last name (required)
        is_active (BooleanField): Whether the user account is active
        date_joined (DateTimeField): Timestamp when the user account was created

    Meta:
        db_table: 'users'
        USERNAME_FIELD: 'email' (uses email for authentication instead of username)
        REQUIRED_FIELDS: ['username', 'first_name', 'last_name']
    """
    email = models.EmailField(
        unique=True,
        help_text="User's unique email address for authentication"
    )
    first_name = models.CharField(
        max_length=150,
        help_text="User's first name"
    )
    last_name = models.CharField(
        max_length=150,
        help_text="User's last name"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Designates whether this user should be treated as active"
    )
    date_joined = models.DateTimeField(
        default=timezone.now,
        help_text="Date and time when the user account was created"
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    objects = UserManager()

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']

    def __str__(self):
        """Return string representation of the user."""
        return self.email

    @property
    def full_name(self):
        """
        Return the user's full name.

        Returns:
            str: User's first and last name combined
        """
        return f"{self.first_name} {self.last_name}".strip()

    def get_full_name(self):
        """
        Return the user's full name (Django's AbstractUser method).

        Returns:
            str: User's first and last name combined, or empty string if not available
        """
        return f"{self.first_name} {self.last_name}".strip()

    def get_display_name(self):
        """
        Get the display name for the user.

        Returns:
            str: Full name if available, otherwise username, otherwise email
        """
        if self.first_name and self.last_name:
            return self.full_name
        elif self.username:
            return self.username
        return self.email


class UserProfile(models.Model):
    """
    Extended user profile information for additional user details.

    This model stores additional information about users that extends beyond
    the basic authentication requirements, including contact information,
    location, and personal details.

    Attributes:
        user (OneToOneField): Link to the User model
        phone (CharField): User's phone number
        address (TextField): User's street address
        city (CharField): User's city
        state (CharField): User's state/province
        country (CharField): User's country
        postal_code (CharField): User's postal/zip code
        date_of_birth (DateField): User's date of birth
        avatar_url (URLField): URL to user's profile picture
        bio (TextField): User's biography or description
        created_at (DateTimeField): Profile creation timestamp
        updated_at (DateTimeField): Last profile update timestamp
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        help_text="User associated with this profile"
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="User's contact phone number"
    )
    address = models.TextField(
        blank=True,
        null=True,
        help_text="User's street address"
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="User's city"
    )
    state = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="User's state or province"
    )
    country = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="User's country"
    )
    postal_code = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="User's postal or zip code"
    )
    date_of_birth = models.DateField(
        blank=True,
        null=True,
        help_text="User's date of birth"
    )
    avatar_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="URL to user's profile picture"
    )
    bio = models.TextField(
        blank=True,
        null=True,
        help_text="User's biography or description"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Profile creation timestamp"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last profile update timestamp"
    )

    class Meta:
        db_table = 'user_profiles'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        """Return string representation of the user profile."""
        return f"{self.user.email}'s Profile"

    @property
    def full_address(self):
        """
        Return the complete formatted address.

        Returns:
            str: Formatted address string with available components
        """
        address_parts = [
            self.address,
            self.city,
            self.state,
            self.postal_code,
            self.country
        ]
        return ', '.join(part for part in address_parts if part)


class JWTToken(models.Model):
    """
    JWT token model for managing user authentication tokens.

    This model tracks JWT tokens issued to users for authentication purposes,
    including token expiration and revocation capabilities for security.

    Attributes:
        user (ForeignKey): User who owns the token
        token_hash (CharField): Hashed version of the JWT token
        expires_at (DateTimeField): Token expiration timestamp
        is_revoked (BooleanField): Whether the token has been revoked
        created_at (DateTimeField): Token creation timestamp
        updated_at (DateTimeField): Last token update timestamp
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='jwt_tokens',
        help_text="User who owns this token"
    )
    token_hash = models.CharField(
        max_length=255,
        unique=True,
        help_text="Hashed version of the JWT token for security"
    )
    expires_at = models.DateTimeField(
        help_text="Timestamp when the token expires"
    )
    is_revoked = models.BooleanField(
        default=False,
        help_text="Whether the token has been manually revoked"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Token creation timestamp"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last token update timestamp"
    )

    class Meta:
        db_table = 'jwt_tokens'
        verbose_name = 'JWT Token'
        verbose_name_plural = 'JWT Tokens'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'expires_at']),
            models.Index(fields=['token_hash']),
            models.Index(fields=['is_revoked']),
        ]

    def __str__(self):
        """Return string representation of the JWT token."""
        return f"Token for {self.user.email}"

    @property
    def is_expired(self):
        """
        Check if the token has expired.

        Returns:
            bool: True if the token has expired, False otherwise
        """
        return timezone.now() > self.expires_at

    @property
    def is_valid(self):
        """
        Check if the token is valid (not expired and not revoked).

        Returns:
            bool: True if the token is valid, False otherwise
        """
        return not (self.is_expired or self.is_revoked)

    def revoke(self):
        """
        Revoke the token by setting is_revoked to True.

        Returns:
            None
        """
        self.is_revoked = True
        self.save(update_fields=['is_revoked', 'updated_at'])
