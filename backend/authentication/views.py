"""
Authentication views for the BuyBuy e-commerce backend.
"""

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User, UserProfile
from .serializers import UserRegistrationSerializer, UserProfileSerializer, UserProfileUpdateSerializer


class RegisterView(generics.CreateAPIView):
    """
    User registration endpoint.
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
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
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                }
            },
            'message': 'User registered successfully'
        }

        return Response(response_data, status=status.HTTP_201_CREATED)

class UserProfileView(generics.RetrieveAPIView):
    """
    Get current user's profile.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserProfileUpdateView(generics.UpdateAPIView):
    """
    Update current user's profile.
    """
    serializer_class = UserProfileUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserListView(generics.ListAPIView):
    """
    List all users (Admin only).
    """
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]


class UserDetailView(generics.RetrieveAPIView):
    """
    Get user details (Admin only).
    """
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]


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
