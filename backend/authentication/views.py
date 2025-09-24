"""
Authentication views for the BuyBuy e-commerce backend.
"""

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
# from rest_framework_simplejwt.tokens import RefreshToken
# from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from .models import User, UserProfile
from django.contrib.auth import get_user_model, logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LogoutView as DjangoLogoutView
from django.shortcuts import redirect, render
from rest_framework.decorators import api_view
from rest_framework import status
from django.contrib.auth.decorators import login_required
# from .serializers import UserRegistrationSerializer, UserProfileSerializer, UserProfileUpdateSerializer
# from .forms import CustomUserCreationForm

User = get_user_model()

def index_view(request):
    return render(request, "index.html")

def users_view(request):
    return render(request, "users.html")

class CustomLoginView(LoginView):
    template_name = "login.html"

@login_required
def products_view(request):
    return render(request, "products.html")

@login_required
def categories_view(request):
    return render(request, "categories.html")

def logout_view(request):
    """
    Session-based logout (for template pages). Clears session and redirects to login.
    Use this if your users log in via Django sessions (LoginView) and you want a simple redirect.
    """
    logout(request)
    return redirect("authentication:login")


@login_required
def users_view(request):
    users = User.objects.all()
    return render(request, "users.html", {"users": users})

from django.contrib.auth.forms import UserCreationForm

def register_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True  # or False if you want admin approval
            user.save()
            return redirect("authentication:login")
    else:
        form = CustomUserCreationForm()
    return render(request, "register.html", {"form": form})


class RegisterView(generics.CreateAPIView):
    """
    User registration endpoint. - SIMPLIFIED
    """
    queryset = User.objects.all()
    # serializer_class = UserRegistrationSerializer  # DISABLED
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        return Response({'message': 'Registration API disabled'}, status=status.HTTP_501_NOT_IMPLEMENTED)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate JWT tokens - DISABLED FOR SIMPLIFIED SETUP
        # refresh = RefreshToken.for_user(user)
        response_data = {
            'success': True,
            'data': {
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'is_active': user.is_active
                },
                # 'tokens': {
                #     'access': str(refresh.access_token),
                #     'refresh': str(refresh)
                # }
            },
            'message': 'User registered successfully'
        }

        return Response(response_data, status=status.HTTP_201_CREATED)

class UserProfileView(generics.RetrieveAPIView):
    """
    Get current user's profile.
    """
    # serializer_class = UserProfileSerializer  # DISABLED
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserProfileUpdateView(generics.UpdateAPIView):
    """
    Update current user's profile.
    """
    # serializer_class = UserProfileUpdateSerializer  # DISABLED
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserListView(generics.ListAPIView):
    """
    List all users (Admin only).
    """
    queryset = User.objects.all()
    # serializer_class = UserProfileSerializer  # DISABLED
    permission_classes = [IsAuthenticated]


class UserDetailView(generics.RetrieveAPIView):
    """
    Get user details (Admin only).
    """
    queryset = User.objects.all()
    # serializer_class = UserProfileSerializer  # DISABLED
    permission_classes = [IsAuthenticated]

class LogoutAPIView(APIView):
    """
    API logout for JWT: blacklists the provided refresh token.
    Request: POST { "refresh": "<refresh_token>" }
    Must be authenticated (access token) if permission_classes include IsAuthenticated.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # DISABLED: JWT token blacklisting
        # refresh_token = request.data.get('refresh')
        # if not refresh_token:
        #     return Response({'detail': 'Refresh token is required.'},
        #                     status=status.HTTP_400_BAD_REQUEST)
        # try:
        #     token = RefreshToken(refresh_token)
        #     # this will raise AttributeError if blacklist app not installed
        #     token.blacklist()
        #     return Response({'detail': 'Logged out successfully.'}, status=status.HTTP_200_OK)
        # except TokenError:
        #     return Response({'detail': 'Token is invalid or expired.'}, status=status.HTTP_400_BAD_REQUEST)
        # except AttributeError:
        #     return Response({
        #         'detail': 'Token blacklisting not enabled. Add '
        #                   '`rest_framework_simplejwt.token_blacklist` to INSTALLED_APPS.'
        #     }, status=status.HTTP_501_NOT_IMPLEMENTED)
        # except Exception as e:
        #     return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'detail': 'Logout endpoint - JWT disabled'}, status=status.HTTP_200_OK)

class UserActivateView(generics.UpdateAPIView):
    """
    Activate user account (Admin only).
    """
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        user = self.get_object()
        user.is_active = True
        user.save()
        return Response({'message': 'User activated successfully'})


class UserDeactivateView(generics.UpdateAPIView):
    """
    Deactivate user account (Admin only).
    """
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response({'message': 'User deactivated successfully'})


class PasswordResetView(generics.GenericAPIView):
    """
    Password reset request endpoint.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        # TODO: Implement password reset logic
        return Response({'message': 'Password reset functionality coming soon'})


class PasswordResetConfirmView(generics.GenericAPIView):
    """
    Password reset confirmation endpoint.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        # TODO: Implement password reset confirmation logic
        return Response({'message': 'Password reset confirmation functionality coming soon'})


class PasswordChangeView(generics.GenericAPIView):
    """
    Password change endpoint for authenticated users.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # TODO: Implement password change logic
        return Response({'message': 'Password change functionality coming soon'})
