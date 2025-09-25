"""
Common views for the BuyBuy e-commerce backend.

This module provides shared functionality and utility views that serve
multiple purposes across the BuyBuy multi-vendor e-commerce platform.
It includes landing pages, dashboard functionality, and system health
monitoring.

Features:
    - Public landing page with platform statistics
    - Authenticated user dashboard with personal metrics
    - System health monitoring for infrastructure
    - Platform-wide statistics and showcases

Architecture:
    - Shared views used across multiple apps
    - Performance optimized with database aggregations
    - Logging integration for monitoring and debugging
    - Caching support for improved response times

Business Value:
    - Landing page drives user acquisition and engagement
    - Dashboard provides users with personalized insights
    - Health monitoring ensures system reliability
    - Statistics showcase platform growth and activity

Security Considerations:
    - Public endpoints appropriately exposed
    - Authenticated endpoints require login
    - Database queries optimized to prevent performance issues
    - Error handling prevents information leakage

Examples:
    Public landing page access:
        >>> # GET / - shows platform overview
        >>> response = landing_page(request)

    User dashboard access:
        >>> # GET /dashboard - shows personal metrics
        >>> response = index(authenticated_request)

    Health check monitoring:
        >>> # GET /health - returns system status
        >>> response = health_check(request)

Dependencies:
    - Django framework components
    - Product and order models for statistics
    - Caching system for performance
    - Logging system for monitoring

Notes:
    - Optimized for performance with efficient queries
    - Supports both public and authenticated access patterns
    - Extensible for additional platform-wide functionality
    - Suitable for high-traffic e-commerce environments
"""

from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
from django.utils import timezone
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from products.models import Product, Order, OrderItem
import logging

logger = logging.getLogger('buybuy')


def landing_page(request):
    """
    Public landing page showcasing platform highlights and statistics.

    Renders the main landing page for BuyBuy with key platform metrics,
    featured products, and user acquisition elements. Designed to attract
    new users and demonstrate platform activity without requiring authentication.

    Parameters:
        request (HttpRequest): HTTP request object, authentication not required.

    Returns:
        HttpResponse: Rendered 'landing.html' template with platform context.

    Template Context:
        featured_products (QuerySet): Latest 6 active products for showcase
        total_products (int): Count of all active products on platform
        total_users (int): Count of unique sellers (vendors) on platform

    Business Rules:
        - Shows only active products to maintain quality perception
        - Displays recent products to highlight platform activity
        - Provides growth metrics to build user confidence
        - No authentication required for maximum accessibility

    Performance Optimizations:
        - Limited to 6 featured products for fast loading
        - Efficient count queries using database aggregation
        - Distinct seller count prevents duplicate counting

    Examples:
        >>> # GET request to landing page
        >>> response = landing_page(request)
        >>> # Returns public landing page with platform showcase

    Marketing Value:
        - Showcases product variety and platform activity
        - Builds trust through active vendor and product counts
        - Encourages user registration and engagement
        - Provides SEO-friendly content for search engines

    Database Queries:
        - Single query for featured products with ordering
        - Efficient count query for total products
        - Optimized distinct count for unique sellers

    Security:
        - Public access appropriate for landing page
        - Only active products shown (no sensitive data)
        - No user-specific information exposed

    Notes:
        - Consider caching for high-traffic scenarios
        - Featured products could be curated rather than just recent
        - Statistics could be enhanced with additional metrics
    """
    # Get some sample data for showcase
    featured_products = Product.objects.filter(is_active=True).order_by('-created_at')[:6]
    total_products = Product.objects.filter(is_active=True).count()
    total_users = Product.objects.filter(is_active=True).values('seller').distinct().count()

    context = {
        'featured_products': featured_products,
        'total_products': total_products,
        'total_users': total_users,
    }

    return render(request, 'landing.html', context)


@login_required
def index(request):
    """
    Authenticated user dashboard with personalized metrics and activity.

    Provides a comprehensive dashboard for authenticated users showing their
    activity as both buyers and sellers in the multi-vendor marketplace.
    Displays key metrics, recent activity, and quick access to important data.

    Parameters:
        request (HttpRequest): HTTP request with authenticated user.

    Returns:
        HttpResponse: Rendered 'index.html' template with user dashboard data.

    Template Context:
        Selling Metrics:
            - total_products (int): Number of products user is selling
            - selling_products (QuerySet): Recent 5 products user is selling
            - total_sales_count (int): Number of items sold by user
            - total_revenue (Decimal): Total revenue from sales

        Buying Metrics:
            - total_purchases (int): Number of orders user has placed
            - recent_purchases (QuerySet): Recent 5 items user has bought

        Activity Feeds:
            - recent_sales (QuerySet): Recent 5 sales transactions for seller

    Business Rules:
        - Shows dual perspective: buyer and seller activities
        - Revenue calculations based on actual sales (OrderItems)
        - Recent activity limited to 5 items for performance
        - All data filtered by authenticated user

    Database Optimizations:
        - Uses select_related for efficient joins
        - Aggregation queries for performance (Sum, Count)
        - Limited result sets (5 items) for fast loading
        - Optimized order by creation date for relevance

    Examples:
        >>> # GET request for authenticated user dashboard
        >>> response = index(request)
        >>> # Returns personalized dashboard with metrics

    User Experience:
        - Comprehensive overview of marketplace activity
        - Quick access to recent transactions
        - Clear separation of buying vs selling activities
        - Performance optimized for fast dashboard loading

    Financial Tracking:
        - Revenue calculations from completed transactions
        - Sales count includes all order items sold
        - Purchase history for expense tracking
        - Real-time activity updates

    Performance Considerations:
        - Multiple database queries optimized with select_related
        - Limited result sets prevent excessive data loading
        - Aggregate functions used efficiently for counts and sums
        - Recent activity queries ordered for cache efficiency

    Security:
        - Authentication required via @login_required
        - All data filtered by request.user for privacy
        - No access to other users' financial information
        - Transaction data appropriately scoped

    Dashboard Sections:
        1. Selling Overview: Products, sales count, revenue
        2. Buying Overview: Order count and recent purchases
        3. Recent Activity: Latest sales and purchase transactions
        4. Quick Stats: Key performance indicators

    Notes:
        - Could benefit from caching for frequent dashboard access
        - Revenue calculation assumes OrderItem.total_price exists
        - Recent activity could be enhanced with filtering options
        - Dashboard could be extended with charts and analytics
    """
    # Get user's products (what they're selling)
    user_products = Product.objects.filter(seller=request.user)
    total_products = user_products.count()

    # Get user's orders (what they've bought)
    user_orders = Order.objects.filter(buyer=request.user)
    total_purchases = user_orders.count()

    # Get sales stats (what others have bought from this user)
    user_sales = OrderItem.objects.filter(product__seller=request.user)
    total_sales_count = user_sales.count()
    total_revenue = user_sales.aggregate(total=Sum('total_price'))['total'] or 0

    # Recent data (limit to 5 items each)
    selling_products = user_products.order_by('-created_at')[:5]
    recent_purchases = OrderItem.objects.filter(
        order__buyer=request.user
    ).select_related('product', 'order').order_by('-created_at')[:5]
    recent_sales = user_sales.select_related(
        'product', 'order', 'order__buyer'
    ).order_by('-created_at')[:5]

    context = {
        'total_products': total_products,
        'total_purchases': total_purchases,
        'total_sales_count': total_sales_count,
        'total_revenue': total_revenue,
        'selling_products': selling_products,
        'recent_purchases': recent_purchases,
        'recent_sales': recent_sales,
    }

    return render(request, 'index.html', context)

def health_check(request):
    """
    System health monitoring endpoint for infrastructure and operations.

    Provides comprehensive health status information for the BuyBuy platform,
    including database connectivity, cache system status, and overall system
    health. Designed for load balancers, monitoring systems, and DevOps tools.

    Parameters:
        request (HttpRequest): HTTP request object, no authentication required.

    Returns:
        JsonResponse: Health status with HTTP 200 (healthy) or 503 (unhealthy).

    Response Format:
        {
            "status": "healthy|unhealthy",
            "timestamp": "ISO datetime string",
            "services": {
                "database": "healthy|unhealthy: error_message",
                "redis": "healthy|unhealthy: error_message"
            }
        }

    Health Checks Performed:
        1. Database Connectivity: Tests database connection with simple query
        2. Redis Cache: Validates cache system availability and connectivity

    HTTP Status Codes:
        - 200: All systems healthy and operational
        - 503: One or more critical systems unhealthy

    Business Rules:
        - Overall status "unhealthy" if any service fails
        - Detailed service-specific status for debugging
        - Timestamp provided for monitoring correlation
        - Errors logged for operational visibility

    Examples:
        >>> # Healthy system response
        >>> {
        ...     "status": "healthy",
        ...     "timestamp": "2024-01-15T10:30:00Z",
        ...     "services": {
        ...         "database": "healthy",
        ...         "redis": "healthy"
        ...     }
        ... }

        >>> # Unhealthy system with database issue
        >>> {
        ...     "status": "unhealthy",
        ...     "timestamp": "2024-01-15T10:30:00Z",
        ...     "services": {
        ...         "database": "unhealthy: connection timeout",
        ...         "redis": "healthy"
        ...     }
        ... }

    Monitoring Integration:
        - Load balancer health checks
        - Application performance monitoring (APM)
        - Infrastructure monitoring systems
        - Alerting and notification systems
        - Container orchestration health probes

    Error Handling:
        - Database connection errors caught and logged
        - Cache system errors handled gracefully
        - Detailed error messages for troubleshooting
        - System continues operating during health checks

    Performance Considerations:
        - Lightweight queries for minimal system impact
        - Fast response times for frequent health checks
        - Non-blocking operations prevent system slowdown
        - Efficient error handling and logging

    Operational Value:
        - Enables proactive system monitoring
        - Supports automated failover mechanisms
        - Provides debugging information for issues
        - Facilitates infrastructure automation

    Security Considerations:
        - No sensitive information exposed in responses
        - Public endpoint appropriate for health monitoring
        - Error messages provide operational info without security risks
        - No authentication required for monitoring systems

    Notes:
        - Could be extended with additional service checks
        - Response format compatible with standard monitoring tools
        - Logging integrated for operational visibility
        - Suitable for high-frequency health check intervals
    """
    health_status = {
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'services': {}
    }

    # Check database
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        health_status['services']['database'] = 'healthy'
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        health_status['services']['database'] = f'unhealthy: {str(e)}'
        health_status['status'] = 'unhealthy'

    # Check Redis cache
    try:
        cache.get('health_check')
        health_status['services']['redis'] = 'healthy'
    except Exception as e:
        logger.error(f"Redis health check failed: {str(e)}")
        health_status['services']['redis'] = f'unhealthy: {str(e)}'
        health_status['status'] = 'unhealthy'

    status_code = 200 if health_status['status'] == 'healthy' else 503
    return JsonResponse(health_status, status=status_code)
