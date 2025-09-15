"""
Admin configuration for authentication app.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile, JWTToken


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom User admin configuration.
    """
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-date_joined',)

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    User Profile admin configuration.
    """
    list_display = ('user', 'phone', 'city', 'country', 'created_at')
    list_filter = ('country', 'city', 'created_at')
    search_fields = ('user__email', 'user__username', 'phone', 'city', 'country')
    ordering = ('-created_at',)

    fieldsets = (
        ('User', {'fields': ('user',)}),
        ('Contact Information', {'fields': ('phone', 'address', 'city', 'state', 'country', 'postal_code')}),
        ('Personal Information', {'fields': ('date_of_birth', 'avatar_url', 'bio')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

    readonly_fields = ('created_at', 'updated_at')


@admin.register(JWTToken)
class JWTTokenAdmin(admin.ModelAdmin):
    """
    JWT Token admin configuration.
    """
    list_display = ('user', 'token_hash', 'expires_at', 'is_revoked', 'created_at')
    list_filter = ('is_revoked', 'expires_at', 'created_at')
    search_fields = ('user__email', 'user__username', 'token_hash')
    ordering = ('-created_at',)

    fieldsets = (
        ('Token Information', {'fields': ('user', 'token_hash', 'expires_at', 'is_revoked')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

    readonly_fields = ('created_at', 'updated_at')
