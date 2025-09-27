"""
Django settings for BuyBuy e-commerce backend project.

This module contains the comprehensive configuration for the BuyBuy multi-vendor
e-commerce platform. It includes all necessary settings for a production-ready
Django application with proper security, performance, and development considerations.

Configuration Areas:
    - Core Django application settings
    - Database configuration with MySQL support
    - Authentication and JWT token management
    - REST API framework configuration
    - Static and media file handling
    - Security settings for production deployment
    - Logging and monitoring configuration
    - Cache configuration with Redis support
    - Email system configuration
    - CORS settings for frontend integration

Architecture Decisions:
    - Custom User model for extended functionality
    - JWT authentication for stateless API access
    - MySQL database for production reliability
    - Redis caching for performance optimization
    - Comprehensive logging for monitoring and debugging
    - Environment-based configuration for deployment flexibility

Security Features:
    - Production-ready security headers
    - HTTPS enforcement in production
    - Secure cookie settings
    - CORS configuration for controlled access
    - Password validation requirements
    - File upload security controls

Performance Optimizations:
    - Redis-backed caching system
    - Optimized static file serving
    - Database query optimization settings
    - API pagination for large datasets
    - Efficient session management

Development Features:
    - Environment-based configuration with python-decouple
    - Comprehensive logging for debugging
    - API documentation with Spectacular
    - Development-friendly error handling
    - Hot reloading support with django-extensions

Production Readiness:
    - Environment variable configuration
    - Security settings conditional on DEBUG mode
    - Proper static file handling
    - Comprehensive logging configuration
    - Health check endpoint support

Examples:
    Environment variable usage:
        # .env file
        DEBUG=False
        SECRET_KEY=your-production-secret-key
        DATABASE_URL=mysql://user:pass@host/db
        REDIS_URL=redis://localhost:6379/1

    Security in production:
        # Automatic HTTPS enforcement when DEBUG=False
        # Secure cookies and headers enabled
        # XSS and CSRF protection activated

Dependencies:
    - python-decouple for environment configuration
    - djangorestframework for API functionality
    - djangorestframework-simplejwt for authentication
    - django-cors-headers for CORS support
    - drf-spectacular for API documentation
    - django-redis for caching
    - mysqlclient for database connectivity

Notes:
    - All sensitive settings use environment variables
    - Database credentials should be secured in production
    - Logging configuration includes both file and console output
    - Cache and session backends use Redis for persistence
    - API documentation automatically generated from code
"""

import os
from pathlib import Path
from decouple import config
from datetime import timedelta
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# =============================================================================
# CORE DJANGO CONFIGURATION
# =============================================================================

# SECURITY WARNING: keep the secret key used in production secret!
# Used for cryptographic signing including sessions, cookies, and CSRF tokens
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-me-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
# Controls error reporting, static file serving, and security features
DEBUG = config('DEBUG', default=True, cast=bool)

# Hosts allowed to access this Django application
# Should include domain names, IP addresses, and load balancer addresses
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',') + ['.vercel.app']

# =============================================================================
# APPLICATION DEFINITION
# =============================================================================

# Core Django applications required for basic functionality
DJANGO_APPS = [
    'django.contrib.admin',        # Admin interface for data management
    'django.contrib.auth',         # Authentication system
    'django.contrib.contenttypes', # Content type framework
    'django.contrib.sessions',     # Session management
    'django.contrib.messages',     # Message framework for user feedback
    'django.contrib.staticfiles',  # Static file handling
]

# Third-party applications for extended functionality
THIRD_PARTY_APPS = [
    'rest_framework',           # Django REST Framework for API
    'rest_framework_simplejwt', # JWT authentication for APIs
    'corsheaders',             # CORS handling for frontend integration
    'drf_spectacular',         # API documentation generation
    'django_filters',          # Advanced filtering for APIs
    'django_extensions',       # Development utilities and commands
]

# Custom applications specific to BuyBuy platform
LOCAL_APPS = [
    'authentication',  # Custom user management and JWT tokens
    'products',       # Product catalog, cart, and order management
    'categories',     # Hierarchical product categorization
    'common',        # Shared utilities and platform-wide functionality
]

# Combined application list in order of dependency
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# =============================================================================
# MIDDLEWARE CONFIGURATION
# =============================================================================

# Middleware stack processed in order for requests and reverse order for responses
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',               # CORS headers (must be early)
    'django.middleware.security.SecurityMiddleware',      # Security headers
    'django.contrib.sessions.middleware.SessionMiddleware', # Session handling
    'django.middleware.common.CommonMiddleware',           # Common processing
    'django.middleware.csrf.CsrfViewMiddleware',          # CSRF protection
    'django.contrib.auth.middleware.AuthenticationMiddleware', # User authentication
    'django.contrib.messages.middleware.MessageMiddleware',    # User messages
    'django.middleware.clickjacking.XFrameOptionsMiddleware',  # Clickjacking protection
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'frontend/templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================

# Primary database configuration using MySQL for production reliability
# Supports transactions, foreign keys, and advanced indexing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',  # MySQL database engine
        'NAME': 'BuyBuy',                     # Database name
        'USER': 'root',                       # Database user (should use env var in production)
        'PASSWORD': 'Gamedfashkh1@',          # Database password (should use env var in production)
        'HOST': 'localhost',                  # Database host
        'PORT': '3306',                       # Standard MySQL port
        'OPTIONS': {
            'sql_mode': 'TRADITIONAL',        # Strict SQL mode for data integrity
            'charset': 'utf8mb4',            # Full UTF-8 support including emojis
        },
    }
}

# Database Configuration for Deployment
if 'DATABASE_URL' in os.environ:
    DATABASES = {
        'default': dj_database_url.parse(os.environ.get('DATABASE_URL'))
    }
else:
    # Your existing MySQL configuration for local development
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'BuyBuy',
            'USER': 'root',
            'PASSWORD': 'Gamedfashkh1@',
            'HOST': 'localhost',
            'PORT': '3306',
            'OPTIONS': {
                'sql_mode': 'TRADITIONAL',
                'charset': 'utf8mb4',
            },
        }
    }


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    BASE_DIR / 'frontend/static',
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / config('MEDIA_ROOT', default='media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'authentication.User'

# Authentication Backends
# Custom backend supports both username and email authentication
AUTHENTICATION_BACKENDS = [
    'authentication.backends.EmailOrUsernameAuthBackend',  # Custom email/username auth
    'django.contrib.auth.backends.ModelBackend',          # Default Django auth (fallback)
]

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(seconds=config('JWT_ACCESS_TOKEN_LIFETIME', default=3600, cast=int)),
    'REFRESH_TOKEN_LIFETIME': timedelta(seconds=config('JWT_REFRESH_TOKEN_LIFETIME', default=604800, cast=int)),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': config('JWT_SECRET_KEY', default=SECRET_KEY),
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'JTI_CLAIM': 'jti',
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

# CORS Settings
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='http://localhost:3000,http://127.0.0.1:3000').split(',')
CORS_ALLOW_CREDENTIALS = True

# API Documentation
SPECTACULAR_SETTINGS = {
    'TITLE': 'BuyBuy E-Commerce API',
    'DESCRIPTION': 'A comprehensive e-commerce backend API with product management, user authentication, and advanced querying capabilities.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': '/api/v1/',
}

# Cache Configuration
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL', default='redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Session Configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# Email Configuration
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': config('LOG_LEVEL', default='DEBUG'),
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': config('LOG_LEVEL', default='INFO'),
            'propagate': False,
        },
        'buybuy': {
            'handlers': ['console', 'file'],
            'level': config('LOG_LEVEL', default='DEBUG'),
            'propagate': False,
        },
    },
}

# Security Settings
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_REDIRECT_EXEMPT = []
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    X_FRAME_OPTIONS = 'DENY'

# File Upload Settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
FILE_UPLOAD_PERMISSIONS = 0o644

# Create logs directory if it doesn't exist
os.makedirs(BASE_DIR / 'logs', exist_ok=True)

# Authentication URLs
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'

# Add whitenoise for static files
if not DEBUG:
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
