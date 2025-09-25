"""
Authentication serializers for the BuyBuy e-commerce backend.

This module provides Django REST Framework serializers for user authentication,
registration, and profile management with comprehensive validation and data handling.
"""

from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import User, UserProfile


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration with validation and profile creation.

    This serializer handles new user registration including password validation,
    confirmation matching, and automatic profile creation.

    Fields:
        username (str): Unique username for the user
        email (str): Unique email address for authentication
        password (str): User's password (write-only, minimum 8 characters)
        password_confirm (str): Password confirmation field (write-only)
        first_name (str): User's first name
        last_name (str): User's last name

    Validation:
        - Ensures password and confirmation match
        - Validates password strength using Django's validators
        - Checks email and username uniqueness
    """
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'},
        help_text='Password must be at least 8 characters long'
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text='Enter the same password as above for verification'
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm', 'first_name', 'last_name')
        extra_kwargs = {
            'email': {'help_text': 'Enter a valid email address for account verification'},
            'username': {'help_text': 'Enter a unique username for your account'},
            'first_name': {'help_text': 'Enter your first name'},
            'last_name': {'help_text': 'Enter your last name'}
        }

    def validate_email(self, value):
        """
        Validate email uniqueness and format.

        Args:
            value (str): Email address to validate

        Returns:
            str: Normalized email address

        Raises:
            ValidationError: If email already exists or is invalid
        """
        if User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError(
                "A user with this email address already exists."
            )
        return value.lower()

    def validate_username(self, value):
        """
        Validate username uniqueness.

        Args:
            value (str): Username to validate

        Returns:
            str: Validated username

        Raises:
            ValidationError: If username already exists
        """
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "A user with this username already exists."
            )
        return value

    def validate_password(self, value):
        """
        Validate password using Django's password validators.

        Args:
            value (str): Password to validate

        Returns:
            str: Validated password

        Raises:
            ValidationError: If password doesn't meet requirements
        """
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value

    def validate(self, attrs):
        """
        Cross-field validation for password confirmation.

        Args:
            attrs (dict): All field data

        Returns:
            dict: Validated data

        Raises:
            ValidationError: If passwords don't match
        """
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': ["Password fields didn't match."]
            })
        return attrs

    def create(self, validated_data):
        """
        Create user with hashed password and profile.

        Args:
            validated_data (dict): Validated user data

        Returns:
            User: Created user instance with profile
        """
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')

        # Create user instance
        user = User(**validated_data)
        user.set_password(password)  # Properly hash the password
        user.save()

        # Create associated user profile
        UserProfile.objects.create(user=user)

        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Basic serializer for user profile information.

    This serializer provides read-only access to basic user information
    for public display and general user data retrieval.

    Fields:
        id: User's unique identifier
        username: User's username
        email: User's email address (read-only)
        first_name: User's first name
        last_name: User's last name
        is_active: User's active status (read-only)
        date_joined: Account creation timestamp (read-only)
        full_name: Computed full name property
    """
    full_name = serializers.CharField(source='full_name', read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'is_active', 'date_joined'
        )
        read_only_fields = ('id', 'username', 'email', 'is_active', 'date_joined')


class ExtendedUserProfileSerializer(serializers.ModelSerializer):
    """
    Extended serializer for user profile with additional profile information.

    This serializer includes detailed user profile information from the
    UserProfile model for comprehensive user data management.

    Fields:
        All basic user fields plus extended profile information:
        - Contact information (phone, address)
        - Location details (city, state, country, postal_code)
        - Personal information (date_of_birth, bio, avatar_url)
        - Timestamps (created_at, updated_at)
    """
    profile = serializers.SerializerMethodField()
    full_name = serializers.CharField(source='full_name', read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'is_active', 'date_joined', 'profile'
        )
        read_only_fields = ('id', 'username', 'email', 'is_active', 'date_joined')

    def get_profile(self, obj):
        """
        Get extended profile information for the user.

        Args:
            obj (User): User instance

        Returns:
            dict or None: Profile data dictionary or None if no profile exists
        """
        try:
            profile = obj.profile
            return {
                'phone': profile.phone,
                'address': profile.address,
                'city': profile.city,
                'state': profile.state,
                'country': profile.country,
                'postal_code': profile.postal_code,
                'date_of_birth': profile.date_of_birth,
                'avatar_url': profile.avatar_url,
                'bio': profile.bio,
                'full_address': profile.full_address,
                'created_at': profile.created_at,
                'updated_at': profile.updated_at,
            }
        except UserProfile.DoesNotExist:
            return None


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile information.

    This serializer allows users to update their basic profile information
    including name fields with proper validation.

    Fields:
        first_name: User's first name
        last_name: User's last name
    """

    class Meta:
        model = User
        fields = ('first_name', 'last_name')

    def validate_first_name(self, value):
        """
        Validate first name field.

        Args:
            value (str): First name to validate

        Returns:
            str: Validated first name

        Raises:
            ValidationError: If first name is empty or invalid
        """
        if not value or not value.strip():
            raise serializers.ValidationError("First name cannot be empty.")
        return value.strip().title()

    def validate_last_name(self, value):
        """
        Validate last name field.

        Args:
            value (str): Last name to validate

        Returns:
            str: Validated last name

        Raises:
            ValidationError: If last name is empty or invalid
        """
        if not value or not value.strip():
            raise serializers.ValidationError("Last name cannot be empty.")
        return value.strip().title()

    def update(self, instance, validated_data):
        """
        Update user instance with validated data.

        Args:
            instance (User): User instance to update
            validated_data (dict): Validated update data

        Returns:
            User: Updated user instance
        """
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.save(update_fields=['first_name', 'last_name'])
        return instance


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user authentication and login.

    This serializer validates user credentials and returns authenticated user
    information. Supports both username and email authentication.

    Fields:
        username (str): Username or email address
        password (str): User's password

    Returns:
        user: Authenticated user instance (available after validation)
    """
    username = serializers.CharField(
        help_text='Enter your username or email address'
    )
    password = serializers.CharField(
        style={'input_type': 'password'},
        help_text='Enter your account password'
    )

    def validate(self, attrs):
        """
        Validate user credentials and authenticate.

        Args:
            attrs (dict): Login credentials

        Returns:
            dict: Validated data with authenticated user

        Raises:
            ValidationError: If credentials are invalid or account is disabled
        """
        username = attrs.get('username')
        password = attrs.get('password')

        if not username or not password:
            raise serializers.ValidationError(
                'Both username/email and password are required.'
            )

        # Support email-based authentication
        if '@' in username:
            try:
                user_obj = User.objects.get(email=username.lower())
                username = user_obj.username
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    'No account found with this email address.'
                )

        user = authenticate(username=username, password=password)

        if not user:
            raise serializers.ValidationError(
                'Invalid username/email or password. Please try again.'
            )

        if not user.is_active:
            raise serializers.ValidationError(
                'Your account has been deactivated. Please contact support.'
            )

        attrs['user'] = user
        return attrs
