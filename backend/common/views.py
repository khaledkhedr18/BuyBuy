"""
Common views for the BuyBuy e-commerce backend.
"""

from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
from django.utils import timezone
from django.shortcuts import render
import logging

logger = logging.getLogger('buybuy')


def index(request):
    """Enhanced dashboard with e-commerce statistics."""
    context = {}
    
    # Only show detailed dashboard if user is authenticated
    if request.user.is_authenticated:
        from products.models import Product
        from orders.models import Order, OrderItem
        from categories.models import Category
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        # Get basic statistics
        context.update({
            'total_products': Product.objects.filter(is_active=True).count(),
            'total_categories': Category.objects.filter(is_active=True).count(),
            'total_users': User.objects.filter(is_active=True).count(),
            'total_orders': Order.objects.count(),
        })
        
        # Get user-specific data
        if hasattr(request.user, 'orders'):
            user_orders = request.user.orders.all()[:5]  # Last 5 orders
            context['recent_orders'] = user_orders
        
        # Get products user is selling (if any)
        if hasattr(request.user, 'products_sold'):
            user_products = request.user.products_sold.filter(is_active=True)[:5]
            context['my_products'] = user_products
        
        # Get recent products
        context['recent_products'] = Product.objects.filter(is_active=True).order_by('-created_at')[:5]
    
    return render(request, 'index.html', context)

def health_check(request):
    """
    Health check endpoint for load balancers and monitoring.
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
