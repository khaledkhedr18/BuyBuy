"""
URL configuration for BuyBuy e-commerce backend project.
"""

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from common.views import index


urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    path('products/', include('products.urls')),
    path('categories/', include('categories.urls')),
    path('users/', include('authentication.user_urls')),


    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),


    # API v1
    path('api/v1/auth/', include('authentication.urls')),
    path('api/v1/products/', include('products.urls')),
    path('api/v1/categories/', include('categories.urls')),
    path('api/v1/users/', include('authentication.user_urls')),

    # Health Check
    path('health/', include('common.urls')),
    re_path(r'^.*$', index, name='index'),

]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    # Debug toolbar
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
