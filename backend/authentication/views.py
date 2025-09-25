"""
Authentication views for the BuyBuy e-commerce backend.

This module provides both template-based and API views for user authentication,
registration, and dashboard functionality including user activity summaries.
"""

from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Sum, Count
from .models import User, UserProfile
from .serializers import UserRegistrationSerializer, UserProfileSerializer
from products.models import Product, Order, OrderItem
from .forms import CustomUserCreationForm, CustomLoginForm


def login_view(request):
    """
    Handle user login with template-based authentication.

    This view processes login requests using Django's built-in authentication
    system with custom forms. Redirects authenticated users to the dashboard.

    Args:
        request (HttpRequest): The HTTP request object

    Returns:
        HttpResponse: Rendered login template or redirect to dashboard

    Template:
        login.html: Login form template with authentication fields
    """
    if request.method == 'POST':
        form = CustomLoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.get_display_name()}!')
                return redirect('authentication:index')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = CustomLoginForm()

    return render(request, 'login.html', {'form': form})


@login_required
def index_view(request):
    """
    Display user dashboard with activity summary and statistics.

    This view provides an overview of the user's e-commerce activity including
    products for sale, recent purchases, sales, and revenue statistics.

    Args:
        request (HttpRequest): The HTTP request object with authenticated user

    Returns:
        HttpResponse: Rendered dashboard template with user activity data

    Context:
        user: Current authenticated user
        selling_products: User's active products for sale (limited to 5)
        recent_purchases: User's recent purchase orders (limited to 5)
        recent_sales: User's recent sales (limited to 5)
        total_products: Total count of user's active products
        total_purchases: Total count of user's purchase orders
        total_sales_count: Total count of user's sales
        total_revenue: Total revenue from user's sales

    Template:
        index.html: Dashboard template displaying user statistics
    """
    user = request.user

    # Get user's products for sale (limit for performance)
    selling_products = Product.objects.filter(
        seller=user,
        is_active=True
    ).select_related('category')[:5]

    # Get user's recent purchases with related data
    recent_purchases = OrderItem.objects.filter(
        order__buyer=user
    ).select_related('product', 'order').order_by('-order__created_at')[:5]

    # Get user's recent sales with buyer information
    recent_sales = OrderItem.objects.filter(
        seller=user
    ).select_related('product', 'order', 'order__buyer').order_by('-order__created_at')[:5]

    # Calculate comprehensive statistics
    total_products = Product.objects.filter(seller=user, is_active=True).count()
    total_purchases = Order.objects.filter(buyer=user).count()
    total_sales = OrderItem.objects.filter(seller=user).aggregate(
        count=Count('id'),
        revenue=Sum('price')
    )

    context = {
        'user': user,
        'selling_products': selling_products,
        'recent_purchases': recent_purchases,
        'recent_sales': recent_sales,
        'total_products': total_products,
        'total_purchases': total_purchases,
        'total_sales_count': total_sales['count'] or 0,
        'total_revenue': total_sales['revenue'] or 0,
    }

    return render(request, 'index.html', context)


@login_required
def products_view(request):
    """
    Display all active products with purchasing capabilities.

    This view shows all available products in the marketplace with the ability
    to add items to the shopping cart. Products are optimized with select_related
    for better database performance.

    Args:
        request (HttpRequest): The HTTP request object with authenticated user

    Returns:
        HttpResponse: Rendered products template with active products list

    Context:
        products: All active products with related category and seller information

    Template:
        products.html: Product listing template with cart functionality
    """
    products = Product.objects.filter(
        is_active=True
    ).select_related('category', 'seller').order_by('-created_at')

    return render(request, 'products.html', {'products': products})


@login_required
def categories_view(request):
    """
    Display all active product categories.

    This view shows all available product categories for browsing and filtering
    products by category.

    Args:
        request (HttpRequest): The HTTP request object with authenticated user

    Returns:
        HttpResponse: Rendered categories template with category list

    Context:
        categories: All active categories available for products

    Template:
        categories.html: Category listing template
    """
    from categories.models import Category
    categories = Category.objects.filter(is_active=True).order_by('name')
    return render(request, "categories.html", {"categories": categories})


@login_required
def users_view(request):
    """
    Display all users in the system (admin functionality).

    This view provides a list of all registered users. Should be restricted
    to admin users only in production environments.

    Args:
        request (HttpRequest): The HTTP request object with authenticated user

    Returns:
        HttpResponse: Rendered users template with user list

    Context:
        users: All registered users in the system

    Template:
        users.html: User listing template

    Note:
        Consider adding proper permission checks for admin-only access
    """
    users = User.objects.all().order_by('-date_joined')
    return render(request, "users.html", {"users": users})


def register_view(request):
    """
    Handle user registration with custom user creation form.

    This view processes new user registrations using a custom form that extends
    Django's user creation functionality with additional required fields.

    Args:
        request (HttpRequest): The HTTP request object

    Returns:
        HttpResponse: Rendered registration template or redirect to login

    Template:
        register.html: User registration form template
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(
                request,
                f'Registration successful! Welcome {user.get_display_name()}. You can now log in.'
            )
            return redirect('authentication:login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()

    return render(request, 'register.html', {'form': form})


class CustomLoginView(APIView):
    """
    API view for JWT token-based authentication.

    This API endpoint handles user login requests and returns JWT tokens
    for API authentication. Supports both username and email login.

    Attributes:
        permission_classes: [AllowAny] - Allow unauthenticated access for login
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Authenticate user and return JWT tokens.

        Args:
            request (Request): DRF request object containing login credentials
                - username (str): User's username or email
                - password (str): User's password

        Returns:
            Response: JSON response with JWT tokens or error message
                Success (200): Contains refresh token, access token, user_id, username
                Error (401): Contains error message for invalid credentials

        Example:
            POST /api/login/
            {
                "username": "user@example.com",
                "password": "password123"
            }

            Response:
            {
                "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "user_id": 1,
                "username": "user@example.com"
            }
        """
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response(
                {'error': 'Username and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(username=username, password=password)
        if user and user.is_active:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': user.full_name
            }, status=status.HTTP_200_OK)

        return Response(
            {'error': 'Invalid credentials or inactive account'},
            status=status.HTTP_401_UNAUTHORIZED
        )


def logout_view(request):
    """
    Handle user logout for template-based authentication.

    This view logs out the current user and redirects to the login page
    with a success message.

    Args:
        request (HttpRequest): The HTTP request object with authenticated user

    Returns:
        HttpResponse: Redirect to login page with logout confirmation message
    """
    user_display_name = request.user.get_display_name() if request.user.is_authenticated else "User"
    logout(request)
    messages.success(request, f'Goodbye {user_display_name}! You have been logged out successfully.')
    return redirect('authentication:login')
