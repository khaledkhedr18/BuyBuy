from django.urls import path
# from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenBlacklistView
from . import views
from .views import (
    index_view, CustomLoginView, products_view, categories_view,
    users_view, register_view, logout_view
)

app_name = 'authentication'

urlpatterns = [
    # Frontend (session-based)
    path("", index_view, name="index"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", logout_view, name="logout"),
    path("register/", register_view, name="register"),
    path("products/", products_view, name="products"),
    path("categories/", categories_view, name="categories"),

    # API (JWT) - DISABLED
    # path('api/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('api/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # path('api/logout/', TokenBlacklistView.as_view(), name='token_blacklist'),

    # API User Registration
    path('api/register/', views.RegisterView.as_view(), name='api_register'),

    # Password Management (API)
    path('api/password/reset/', views.PasswordResetView.as_view(), name='password_reset'),
    path('api/password/reset/confirm/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('api/password/change/', views.PasswordChangeView.as_view(), name='password_change'),
]
