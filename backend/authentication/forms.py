"""
Authentication forms for the BuyBuy e-commerce backend.

This module provides custom forms for user registration and authentication
with enhanced validation and user experience features.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .models import User


class CustomUserCreationForm(UserCreationForm):
    """
    Custom user creation form extending Django's UserCreationForm.

    This form includes additional fields required for user registration
    in the BuyBuy e-commerce platform, including email validation and
    enhanced field styling.

    Fields:
        email: User's email address (required, unique)
        username: User's username (required)
        first_name: User's first name (required)
        last_name: User's last name (required)
        password1: Password field with validation
        password2: Password confirmation field
    """

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address',
            'autocomplete': 'email'
        }),
        help_text='Enter a valid email address. This will be used for login.'
    )

    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your first name',
            'autocomplete': 'given-name'
        }),
        help_text='Your first name as it should appear on the platform.'
    )

    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your last name',
            'autocomplete': 'family-name'
        }),
        help_text='Your last name as it should appear on the platform.'
    )

    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Choose a unique username',
            'autocomplete': 'username'
        }),
        help_text='Choose a unique username. Letters, digits and @/./+/-/_ only.'
    )

    class Meta:
        model = User
        fields = ("email", "username", "first_name", "last_name", "password1", "password2")

    def __init__(self, *args, **kwargs):
        """Initialize form with enhanced styling and attributes."""
        super().__init__(*args, **kwargs)

        # Apply consistent styling to password fields
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter a secure password',
            'autocomplete': 'new-password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm your password',
            'autocomplete': 'new-password'
        })

        # Update help texts for better UX
        self.fields['password1'].help_text = (
            'Your password must contain at least 8 characters and cannot be '
            'too similar to your other personal information.'
        )

    def clean_email(self):
        """
        Validate that the email is unique and properly formatted.

        Returns:
            str: Cleaned email address

        Raises:
            ValidationError: If email already exists or is invalid
        """
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise ValidationError(
                "A user with this email address already exists. "
                "Please use a different email or try logging in."
            )
        return email.lower()

    def clean_username(self):
        """
        Validate that the username is unique and meets requirements.

        Returns:
            str: Cleaned username

        Raises:
            ValidationError: If username already exists or is invalid
        """
        username = self.cleaned_data.get('username')
        if username and User.objects.filter(username=username).exists():
            raise ValidationError(
                "This username is already taken. Please choose a different one."
            )
        return username

    def save(self, commit=True):
        """
        Save the user with additional field validation.

        Args:
            commit (bool): Whether to save the user to the database

        Returns:
            User: The created user instance
        """
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]

        if commit:
            user.save()

        return user


class CustomLoginForm(AuthenticationForm):
    """
    Custom authentication form extending Django's AuthenticationForm.

    This form provides enhanced styling and user experience for the login
    process, supporting both username and email authentication.

    Fields:
        username: Username or email address field with enhanced styling
        password: Password field with enhanced styling and security attributes
    """

    username = forms.CharField(
        max_length=254,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your username or email',
            'autocomplete': 'username',
            'autofocus': True
        }),
        help_text='Enter your username or email address.'
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password',
            'autocomplete': 'current-password'
        }),
        help_text='Enter your account password.'
    )

    def __init__(self, *args, **kwargs):
        """Initialize form with enhanced error handling."""
        super().__init__(*args, **kwargs)

        # Customize error messages
        self.error_messages.update({
            'invalid_login': (
                'Please enter a correct username/email and password. '
                'Note that both fields may be case-sensitive.'
            ),
            'inactive': 'This account is inactive. Please contact support.',
        })

    def clean_username(self):
        """
        Clean username field for authentication.

        Returns:
            str: Cleaned username or email (unchanged, let backend handle it)
        """
        username = self.cleaned_data.get('username')
        if username:
            return username.strip()
        return username
