"""
URL configuration for user management endpoints.
"""

from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # User Profile
    path('page/', views.users_view, name='users'),
    path('profile/', views.UserProfileView.as_view(), name='user_profile'),
    path('profile/update/', views.UserProfileUpdateView.as_view(), name='user_profile_update'),

    # User Management (Admin only)
    path('', views.UserListView.as_view(), name='user_list'),
    path('<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),
    path('<int:pk>/activate/', views.UserActivateView.as_view(), name='user_activate'),
    path('<int:pk>/deactivate/', views.UserDeactivateView.as_view(), name='user_deactivate'),
]
