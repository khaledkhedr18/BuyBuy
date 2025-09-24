"""
Authentication views for the BuyBuy e-commerce backend.
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
    if request.method == 'POST':
        form = CustomLoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('authentication:index')  # Redirect to dashboard (index)
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = CustomLoginForm()

    return render(request, 'login.html', {'form': form})

@login_required
def index_view(request):
    """Dashboard view showing user's activity summary."""
    user = request.user

    # Get user's products for sale
    selling_products = Product.objects.filter(seller=user, is_active=True)[:5]

    # Get user's recent purchases
    recent_purchases = OrderItem.objects.filter(
        order__buyer=user
    ).select_related('product', 'order')[:5]

    # Get user's recent sales
    recent_sales = OrderItem.objects.filter(
        seller=user
    ).select_related('product', 'order', 'order__buyer')[:5]

    # Calculate stats
    total_products = selling_products.count()
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
    """View all products with ability to add to cart."""
    products = Product.objects.filter(is_active=True).select_related('category', 'seller')
    return render(request, 'products.html', {'products': products})

@login_required
def categories_view(request):
    """View all categories."""
    from categories.models import Category
    categories = Category.objects.filter(is_active=True)
    return render(request, "categories.html", {"categories": categories})

@login_required
def users_view(request):
    """View all users (admin only)."""
    users = User.objects.all()
    return render(request, "users.html", {"users": users})

def register_view(request):
    """User registration view."""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('authentication:login')
    else:
        form = CustomUserCreationForm()

    return render(request, 'register.html', {'form': form})

class CustomLoginView(APIView):
    """Custom login view."""
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user_id': user.id,
                    'username': user.username
                })

        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )

def logout_view(request):
    """User logout view."""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('authentication:login')
