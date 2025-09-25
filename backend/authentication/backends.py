"""
Custom authentication backend for the BuyBuy e-commerce platform.

This module provides authentication backends that support both username
and email authentication for enhanced user experience.
"""

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


class EmailOrUsernameAuthBackend(BaseBackend):
    """
    Custom authentication backend that allows login with either email or username.

    This backend enables users to authenticate using either their username
    or email address, providing a more flexible login experience.

    Methods:
        authenticate: Authenticate user with username or email and password
        get_user: Retrieve user by ID for session management

    Example:
        # User can login with either:
        # - username: 'johndoe123' + password
        # - email: 'john@example.com' + password
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate user using either username or email.

        Args:
            request (HttpRequest): The HTTP request object
            username (str): Username or email address
            password (str): User's password
            **kwargs: Additional authentication parameters

        Returns:
            User or None: Authenticated user instance or None if authentication fails

        Examples:
            # Authentication with email
            user = authenticate(username='user@example.com', password='pass123')

            # Authentication with username
            user = authenticate(username='johndoe', password='pass123')
        """
        if username is None or password is None:
            return None

        try:
            # Try to find user by email or username
            user = User.objects.get(
                Q(email=username.lower()) | Q(username=username.lower())
            )

            # Check if the password is correct
            if user.check_password(password) and user.is_active:
                return user

        except User.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a non-existing user
            User().set_password(password)
            return None

        return None

    def get_user(self, user_id):
        """
        Retrieve user by ID for session management.

        Args:
            user_id (int): The user's primary key

        Returns:
            User or None: User instance if found, None otherwise
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
