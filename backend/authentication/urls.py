from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenBlacklistView
from . import views
from .views import (
    index_view, CustomLoginView, login_view, products_view, categories_view,
    users_view, register_view, logout_view
)

app_name = 'authentication'

urlpatterns = [
    # Frontend (session-based)
    path("", index_view, name="index"),  # This will be accessed via /dashboard/
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("register/", register_view, name="register"),
    path("products/", products_view, name="products"),
    path("categories/", categories_view, name="categories"),

    # API (JWT)
    path('api/login/', CustomLoginView.as_view(), name='api_login'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/logout/', TokenBlacklistView.as_view(), name='token_blacklist'),
]
