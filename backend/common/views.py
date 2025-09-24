"""
Common views for the BuyBuy e-commerce backend.
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
    Public landing page for BuyBuy - no authentication required.
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
