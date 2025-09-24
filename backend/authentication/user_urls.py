"""
URL configuration for user management endpoints.
"""

from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # User management page
    path('', views.users_view, name='users'),
]
